from logging import Logger

from azure.ai.evaluation import AzureOpenAIModelConfiguration, ContentSafetyEvaluator, QAEvaluator
from azure.ai.evaluation._evaluators._common._base_eval import EvaluatorBase
from azure.ai.evaluation._model_configurations import AzureAIProject, EvaluatorConfig
from azure.ai.projects.aio import AIProjectClient
from azure.identity import DefaultAzureCredential
from lagom import Container, Singleton
from lagom.interfaces import ReadableContainer

from ai_evaluator.config.configuration import Configuration
from ai_evaluator.config.logs import LoggingConfig
from ai_evaluator.config.os_environ.azure_ai_hub_project import AzureAIHubProjectSettings
from ai_evaluator.config.os_environ.azure_openai import AzureOpenAISettings
from ai_evaluator.config.os_environ.settings import Settings
from ai_evaluator.config.os_environ.utils import load_dotenv_files


def create_foundry_project_client(container: ReadableContainer) -> AIProjectClient:
    settings = container[Settings]
    if not settings.azure_ai_foundry_project_endpoint:
        raise ValueError("azure_ai_project_endpoint is not set in environment variables.")

    return AIProjectClient(
        endpoint=settings.azure_ai_foundry_project_endpoint,
        credential=container[DefaultAzureCredential],  # pyright: ignore[reportArgumentType]
    )


def get_azure_ai_foundry_project(container: ReadableContainer) -> str:
    # oAzureAIProjectSettings = container[AzureAIProjectSettings]
    # return oAzureAIProjectSettings.model_dump()

    settings = container[Settings]  # FIXME? get from AIProjectClient?

    if not settings.azure_ai_foundry_project_endpoint:
        raise ValueError("azure_ai_foundry_project_endpoint is not set in environment variables.")

    return settings.azure_ai_foundry_project_endpoint


container = Container()

load_dotenv_files()  # FIXME? move to main.py?

container[Configuration] = Singleton(Configuration())
container[LoggingConfig] = lambda c: c[Configuration].logging
container[Logger] = lambda c: c[LoggingConfig].logger

container[Settings] = lambda c: c[Configuration].settings
container[AzureOpenAISettings] = lambda c: c[Settings].azure_openai
container[AzureAIHubProjectSettings] = lambda c: c[Settings].azure_ai_hub_project

container[DefaultAzureCredential] = DefaultAzureCredential

# Using Azure AI Hub
container[AzureAIProject] = lambda c: AzureAIProject(
    subscription_id=c[AzureAIHubProjectSettings].subscription_id,
    resource_group_name=c[AzureAIHubProjectSettings].resource_group_name,
    project_name=c[AzureAIHubProjectSettings].project_name,
)

# Using Azure AI Foundry Hub
# container[AIProjectClient] = lambda c: AIProjectClient(
#     credential=c[DefaultAzureCredential],  # pyright: ignore[reportArgumentType]
#     endpoint=c[AzureAIProjectSettings].endpoint or "",
#     subscription_id=c[AzureAIProjectSettings].subscription_id,
#     resource_group_name=c[AzureAIProjectSettings].resource_group_name,
#     project_name=c[AzureAIProjectSettings].project_name,
# )

# Using Azure AI Foundry Connection
container[AIProjectClient] = create_foundry_project_client

# TODO use Connection settings. # NOTE: Connection is async tho
# fmt: off
container[AzureOpenAIModelConfiguration] = lambda c: AzureOpenAIModelConfiguration(
    azure_endpoint=c[AzureOpenAISettings].base_url,
    api_key=c[AzureOpenAISettings].api_key,  # FIXME use Connection instead
    azure_deployment=c[AzureOpenAISettings].deployment_name,
    api_version=c[AzureOpenAISettings].api_version)
# fmt: on


# SRC: https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/evaluate-sdk#composite-evaluators
# NOTE: Includes
# - CoherenceEvaluator
# - FluencyEvaluator
# - F1ScoreEvaluator
# - GroundednessEvaluator
# - RelevanceEvaluator
# - SimilarityEvaluator
container[QAEvaluator] = lambda c: QAEvaluator(model_config=c[AzureOpenAIModelConfiguration])

# container[GroundednessEvaluator] = lambda c: GroundednessEvaluator(model_config=c[AzureOpenAIModelConfiguration])


# SRC: https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/evaluate-sdk#composite-evaluators
# NOTE: Includes
# - HateUnfairnessEvaluator
# - SelfHarmEvaluator
# - SexualEvaluator
# - ViolenceEvaluator
container[ContentSafetyEvaluator] = lambda c: ContentSafetyEvaluator(
    credential=c[DefaultAzureCredential],
    azure_ai_project=get_azure_ai_foundry_project(c),
)

# container[ViolenceEvaluator] = lambda c: ViolenceEvaluator(
#     credential=c[DefaultAzureCredential],
#     azure_ai_project=get_azure_ai_foundry_project(c),
# )

# SRC: https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/evaluate-sdk#evaluator-parameter-format
container[dict[str, EvaluatorBase[str | float]]] = lambda c: {
    "qa": c[QAEvaluator],
    # "groundedness": c[GroundednessEvaluator],
    #
    "content_safety": c[ContentSafetyEvaluator],
    # "violence": c[ViolenceEvaluator],
}

container[dict[str, EvaluatorConfig]] = lambda c: {
    "groundedness": {  # EvaluatorConfig(  # TODO TypedDict
        "query": "${data.queries}",
        "context": "${data.context}",
        "response": "${data.response}",
    }
}
