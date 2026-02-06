"""Charlie Munger's mental models and thinking frameworks."""

from dataclasses import dataclass
from enum import Enum


class ModelCategory(str, Enum):
    """Categories of mental models."""

    PSYCHOLOGY = "psychology"
    ECONOMICS = "economics"
    MATHEMATICS = "mathematics"
    PHYSICS = "physics"
    BIOLOGY = "biology"
    ENGINEERING = "engineering"
    PHILOSOPHY = "philosophy"
    BUSINESS = "business"


@dataclass
class MentalModel:
    """A mental model with its description and application."""

    name: str
    category: ModelCategory
    description: str
    application: str
    munger_quote: str | None = None


# Core Mental Models from Charlie Munger's Latticework
MENTAL_MODELS: list[MentalModel] = [
    # Psychology
    MentalModel(
        name="Incentives",
        category=ModelCategory.PSYCHOLOGY,
        description="People respond to incentives. Never think about what people should do, think about what they will do given their incentives.",
        application="Analyze the incentive structure before judging behavior. 'Show me the incentive and I'll show you the outcome.'",
        munger_quote="Never, ever, think about something else when you should be thinking about the power of incentives.",
    ),
    MentalModel(
        name="Denial",
        category=ModelCategory.PSYCHOLOGY,
        description="The tendency to deny reality when it's too painful or inconvenient to accept.",
        application="Watch for situations where you or others might be avoiding uncomfortable truths.",
        munger_quote="The first principle is that you must not fool yourself - and you are the easiest person to fool.",
    ),
    MentalModel(
        name="Social Proof",
        category=ModelCategory.PSYCHOLOGY,
        description="People look to what others are doing to determine correct behavior.",
        application="Be skeptical of crowd behavior. What's popular isn't always right.",
        munger_quote="When everybody is buying something, that's often the exact wrong time to buy it.",
    ),
    MentalModel(
        name="Consistency and Commitment",
        category=ModelCategory.PSYCHOLOGY,
        description="Once we make a commitment, we tend to be consistent with that commitment, even when wrong.",
        application="Be willing to change your mind when facts change. Avoid escalation of commitment.",
        munger_quote="The human mind is a lot like the human egg, and the human egg has a shut-off device.",
    ),
    MentalModel(
        name="Reciprocity",
        category=ModelCategory.PSYCHOLOGY,
        description="We feel obligated to repay favors, even when unsolicited.",
        application="Be aware of reciprocity in negotiations and relationships. Don't let gifts cloud judgment.",
    ),
    MentalModel(
        name="Envy and Jealousy",
        category=ModelCategory.PSYCHOLOGY,
        description="Envy is one of the most destructive emotions, driving irrational behavior.",
        application="Don't compare yourself to others. Focus on your own goals and progress.",
        munger_quote="The world is not driven by greed; it's driven by envy.",
    ),
    MentalModel(
        name="Authority Bias",
        category=ModelCategory.PSYCHOLOGY,
        description="The tendency to attribute greater accuracy to the opinion of authority figures.",
        application="Evaluate arguments on their merits, not on who's making them.",
    ),
    MentalModel(
        name="Liking/Loving Tendency",
        category=ModelCategory.PSYCHOLOGY,
        description="We distort facts and ignore faults of people we like.",
        application="Try to evaluate people and ideas objectively, regardless of personal feelings.",
    ),

    # Economics
    MentalModel(
        name="Opportunity Cost",
        category=ModelCategory.ECONOMICS,
        description="The true cost of something is what you give up to get it.",
        application="Always consider what you're NOT doing when you choose to do something.",
        munger_quote="Intelligent people make decisions based on opportunity costs.",
    ),
    MentalModel(
        name="Comparative Advantage",
        category=ModelCategory.ECONOMICS,
        description="Focus on what you do relatively better, not absolutely better.",
        application="Specialize in your strengths. Outsource or delegate areas where others have advantage.",
    ),
    MentalModel(
        name="Supply and Demand",
        category=ModelCategory.ECONOMICS,
        description="Prices are determined by the interaction of supply and demand.",
        application="Understand market dynamics before making decisions. Scarcity drives value.",
    ),
    MentalModel(
        name="Compound Interest",
        category=ModelCategory.ECONOMICS,
        description="Small gains compound into large gains over time.",
        application="Start early, be patient. The power is in the time, not the rate.",
        munger_quote="The first rule of compounding: Never interrupt it unnecessarily.",
    ),

    # Mathematics
    MentalModel(
        name="Inversion",
        category=ModelCategory.MATHEMATICS,
        description="Instead of thinking about how to succeed, think about how to avoid failure.",
        application="Invert problems. What would guarantee failure? Avoid those things.",
        munger_quote="Invert, always invert.",
    ),
    MentalModel(
        name="Margin of Safety",
        category=ModelCategory.MATHEMATICS,
        description="Build a buffer against errors and bad luck.",
        application="Never bet the farm. Always maintain reserves for unexpected events.",
        munger_quote="Proper preparation for improbable events.",
    ),
    MentalModel(
        name="Base Rates",
        category=ModelCategory.MATHEMATICS,
        description="The general probability of an outcome regardless of specific case details.",
        application="Before evaluating specifics, consider how similar situations typically turn out.",
    ),
    MentalModel(
        name="Power Laws (Pareto)",
        category=ModelCategory.MATHEMATICS,
        description="A small number of causes often account for most of the effects.",
        application="Focus on the vital few, not the trivial many. 80/20 principle.",
    ),

    # Physics
    MentalModel(
        name="Critical Mass",
        category=ModelCategory.PHYSICS,
        description="Systems need to reach a threshold before effects become visible.",
        application="Be patient with investments that haven't yet reached critical mass.",
    ),
    MentalModel(
        name="Momentum",
        category=ModelCategory.PHYSICS,
        description="Objects in motion tend to stay in motion.",
        application="Understand that trends often continue longer than expected.",
    ),

    # Biology
    MentalModel(
        name="Evolution",
        category=ModelCategory.BIOLOGY,
        description="Adaptation through variation and selection.",
        application="What survives isn't always the strongest, but the most adaptable.",
    ),
    MentalModel(
        name="Red Queen Effect",
        category=ModelCategory.BIOLOGY,
        description="You must keep running just to stay in place.",
        application="In competitive environments, you must continuously improve to maintain position.",
    ),

    # Engineering
    MentalModel(
        name="Redundancy",
        category=ModelCategory.ENGINEERING,
        description="Having backup systems prevents complete failure.",
        application="Build redundancy into critical systems and plans.",
    ),
    MentalModel(
        name="Feedback Loops",
        category=ModelCategory.ENGINEERING,
        description="Outputs of a system become inputs that affect future outputs.",
        application="Identify and leverage positive feedback loops. Break negative ones.",
    ),

    # Philosophy
    MentalModel(
        name="Circle of Competence",
        category=ModelCategory.PHILOSOPHY,
        description="Know what you know and what you don't know.",
        application="Stay within your circle. Expand it deliberately over time.",
        munger_quote="Know the edge of your competency. It's not a competency if you don't know the edge of it.",
    ),
    MentalModel(
        name="First Principles",
        category=ModelCategory.PHILOSOPHY,
        description="Break down complex problems into basic elements and rebuild from there.",
        application="Don't rely on analogies. Understand the fundamental truths.",
    ),
    MentalModel(
        name="Occam's Razor",
        category=ModelCategory.PHILOSOPHY,
        description="The simplest explanation is usually the correct one.",
        application="Prefer simple solutions over complex ones when equally effective.",
    ),

    # Business
    MentalModel(
        name="Moats",
        category=ModelCategory.BUSINESS,
        description="Sustainable competitive advantages that protect against competition.",
        application="Identify and strengthen moats. Avoid businesses without them.",
        munger_quote="We're trying to find a business with a wide and long-lasting moat.",
    ),
    MentalModel(
        name="Scale Economies",
        category=ModelCategory.BUSINESS,
        description="Cost advantages from operating at larger scale.",
        application="Understand how scale affects your business or investments.",
    ),
    MentalModel(
        name="Network Effects",
        category=ModelCategory.BUSINESS,
        description="Value increases as more people use the product.",
        application="Seek businesses with strong network effects. They compound.",
    ),
]


def get_model_by_name(name: str) -> MentalModel | None:
    """Get a mental model by name (case-insensitive)."""
    name_lower = name.lower()
    for model in MENTAL_MODELS:
        if model.name.lower() == name_lower:
            return model
    return None


def get_models_by_category(category: ModelCategory) -> list[MentalModel]:
    """Get all mental models in a category."""
    return [m for m in MENTAL_MODELS if m.category == category]


def get_relevant_models(context: str) -> list[MentalModel]:
    """Get mental models potentially relevant to a given context."""
    # Simple keyword matching - could be enhanced with embeddings
    context_lower = context.lower()
    relevant = []

    keywords = {
        "money": ["Compound Interest", "Margin of Safety", "Opportunity Cost"],
        "invest": ["Compound Interest", "Margin of Safety", "Base Rates", "Moats"],
        "career": ["Opportunity Cost", "Circle of Competence", "Comparative Advantage"],
        "decision": ["Inversion", "Base Rates", "First Principles"],
        "relationship": ["Reciprocity", "Incentives", "Liking/Loving Tendency"],
        "negotiate": ["Incentives", "Reciprocity", "First Principles"],
        "mistake": ["Inversion", "Denial", "Consistency and Commitment"],
        "risk": ["Margin of Safety", "Base Rates", "Redundancy"],
        "competition": ["Moats", "Red Queen Effect", "Comparative Advantage"],
        "team": ["Incentives", "Social Proof", "Authority Bias"],
        "habit": ["Consistency and Commitment", "Feedback Loops", "Momentum"],
    }

    matched_names = set()
    for keyword, models in keywords.items():
        if keyword in context_lower:
            matched_names.update(models)

    for name in matched_names:
        model = get_model_by_name(name)
        if model:
            relevant.append(model)

    # If no specific matches, return core models
    if not relevant:
        core_names = ["Inversion", "Incentives", "Circle of Competence", "Margin of Safety"]
        relevant = [get_model_by_name(n) for n in core_names if get_model_by_name(n)]

    return relevant


def format_models_for_prompt(models: list[MentalModel]) -> str:
    """Format mental models for inclusion in a prompt."""
    lines = ["Relevant Mental Models to Consider:"]
    for model in models:
        lines.append(f"\n**{model.name}** ({model.category.value})")
        lines.append(f"  - {model.description}")
        lines.append(f"  - Application: {model.application}")
        if model.munger_quote:
            lines.append(f'  - Munger: "{model.munger_quote}"')
    return "\n".join(lines)
