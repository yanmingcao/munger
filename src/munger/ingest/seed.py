"""Seed data with Charlie Munger's wisdom."""

from munger.core.models import MungerWisdom, WisdomCategory
from munger.db.vector_store import WisdomVectorStore


def seed_munger_wisdom() -> int:
    """
    Seed the vector store with built-in Charlie Munger wisdom.

    Returns:
        Number of wisdom entries added
    """
    store = WisdomVectorStore()

    # Check if already seeded
    if store.get_count() > 0:
        return 0

    wisdom_items = []

    # Add quotes
    wisdom_items.extend(_get_quotes())

    # Add mental model explanations
    wisdom_items.extend(_get_mental_model_wisdom())

    # Add principles
    wisdom_items.extend(_get_principles())

    # Add speech excerpts
    wisdom_items.extend(_get_speech_excerpts())

    # Batch add to vector store
    store.add_wisdom_batch(wisdom_items)

    return len(wisdom_items)


def _get_quotes() -> list[MungerWisdom]:
    """Get Charlie Munger quotes."""
    quotes = [
        # On Thinking
        ("Invert, always invert.", "On problem solving", ["thinking", "mental_models"]),
        ("I never allow myself to have an opinion on anything that I don't know the other side's argument better than they do.", "On intellectual honesty", ["thinking", "humility"]),
        ("The best thing a human being can do is to help another human being know more.", "On teaching", ["wisdom", "relationships"]),
        ("Take a simple idea and take it seriously.", "On focus", ["wisdom", "simplicity"]),
        ("Spend each day trying to be a little wiser than you were when you woke up.", "On continuous learning", ["learning", "self-improvement"]),
        ("In my whole life, I have known no wise people who didn't read all the time - none, zero.", "On reading", ["learning", "wisdom"]),
        ("You don't have to be brilliant, only a little bit wiser than the other guys, on average, for a long time.", "On compounding wisdom", ["wisdom", "patience"]),

        # On Investing
        ("The big money is not in the buying and selling, but in the waiting.", "On patience in investing", ["investing", "patience"]),
        ("All intelligent investing is value investing.", "On value investing", ["investing"]),
        ("A great business at a fair price is superior to a fair business at a great price.", "On quality", ["investing", "business"]),
        ("The first rule of compounding: Never interrupt it unnecessarily.", "On compounding", ["investing", "patience"]),
        ("We have three baskets for investing: in, out, and too tough to understand.", "On circle of competence", ["investing", "mental_models"]),
        ("Mimicking the herd invites regression to the mean.", "On independent thinking", ["investing", "psychology"]),

        # On Psychology and Behavior
        ("Show me the incentive and I will show you the outcome.", "On incentives", ["psychology", "mental_models"]),
        ("The world is not driven by greed; it's driven by envy.", "On envy", ["psychology"]),
        ("I think I've been in the top 5% of my age cohort all my life in understanding the power of incentives, and all my life I've underestimated it.", "On incentives power", ["psychology", "mental_models"]),
        ("Envy is a really stupid sin because it's the only one you could never possibly have any fun at.", "On envy", ["psychology", "wisdom"]),
        ("The iron rule of nature is: you get what you reward for. If you want ants to come, you put sugar on the floor.", "On incentives", ["psychology"]),

        # On Character
        ("Remember that reputation and integrity are your most valuable assets - and can be lost in a heartbeat.", "On integrity", ["character", "wisdom"]),
        ("You want to deliver to the world what you would buy if you were on the other end.", "On ethics", ["character", "business"]),
        ("Trust is one of the best of all simplifiers, like a lubrication mechanism in an old Swiss clock.", "On trust", ["character", "relationships"]),
        ("The safest way to get what you want is to deserve what you want.", "On deserving", ["character", "success"]),

        # On Mistakes and Learning
        ("I like people admitting they were complete stupid horses' asses. I know I'll perform better if I rub my nose in my mistakes.", "On learning from mistakes", ["learning", "humility"]),
        ("Knowing what you don't know is more useful than being brilliant.", "On intellectual humility", ["wisdom", "mental_models"]),
        ("There is no better teacher than history in determining the future.", "On history", ["learning", "wisdom"]),
        ("I believe in the discipline of mastering the best that other people have ever figured out. I don't believe in just sitting down and trying to dream it all up yourself.", "On learning from others", ["learning"]),

        # On Life and Relationships
        ("The best thing to do with a spouse is to find someone who has low expectations.", "On marriage", ["relationships", "wisdom"]),
        ("I don't think you can get to be a really good investor over a broad range without doing a massive amount of reading.", "On reading", ["learning", "investing"]),
        ("Three rules for a career: Don't sell anything you wouldn't buy yourself. Don't work for anyone you don't respect and admire. Work only with people you enjoy.", "On career", ["career", "character"]),
        ("Develop into a lifelong self-learner through voracious reading; cultivate curiosity and strive to become a little wiser every day.", "On self-development", ["learning", "wisdom"]),

        # On Business
        ("There are two types of businesses: The first earns 12% and you can take it out at the end of the year. The second earns 12%, but all the excess cash must be reinvested. The first is a winner, the second is a loser.", "On capital allocation", ["business", "investing"]),
        ("In business we often find that the winning system goes almost ridiculously far in maximizing and or minimizing one or a few variables.", "On focus", ["business", "strategy"]),
        ("Acknowledging what you don't know is the dawning of wisdom.", "On self-awareness", ["wisdom", "mental_models"]),

        # On Multidisciplinary Thinking
        ("You must know the big ideas in the big disciplines and use them routinely - all of them, not just a few.", "On mental models", ["mental_models", "learning"]),
        ("To the man with only a hammer, every problem looks like a nail.", "On mental models", ["mental_models", "thinking"]),
        ("I constantly see people rise in life who are not the smartest, sometimes not even the most diligent, but they are learning machines.", "On continuous learning", ["learning", "success"]),
    ]

    return [
        MungerWisdom(
            category=WisdomCategory.QUOTE,
            title=context,
            content=quote,
            source="Charlie Munger - Various speeches and interviews",
            tags=tags,
            related_models=[],
        )
        for quote, context, tags in quotes
    ]


def _get_mental_model_wisdom() -> list[MungerWisdom]:
    """Get wisdom about mental models."""
    models = [
        (
            "Inversion",
            "Instead of asking how to succeed, ask how to fail and avoid those things. "
            "All I want to know is where I'm going to die, so I'll never go there. "
            "It's not enough to think about problems forward. You must also think about them backward. "
            "Many hard problems are best solved when they are addressed backward.",
            ["thinking", "problem_solving"],
            ["First Principles", "Margin of Safety"],
        ),
        (
            "Circle of Competence",
            "Know what you know and what you don't know. The most important thing is to know where the perimeter is. "
            "It's not a competency if you don't know the edge of it. If you play games where other people have aptitudes and you don't, "
            "you're going to lose. You have to figure out where you've got an edge. And you've got to play within your circle of competence.",
            ["investing", "self_awareness"],
            ["Incentives", "Opportunity Cost"],
        ),
        (
            "Incentives",
            "Never, ever, think about something else when you should be thinking about the power of incentives. "
            "The most important thing in any economy is the incentive structure. People respond to incentives. "
            "Never think about what people should do; think about what they will do given their incentives. "
            "If you want to predict behavior, you need to understand the incentive structure first.",
            ["psychology", "economics"],
            ["Social Proof", "Authority"],
        ),
        (
            "Margin of Safety",
            "The whole secret of investment is to find places where it's safe and wise to non-diversify. "
            "You need a margin of safety in case things go wrong. Engineering has backup systems. "
            "You should too. Build redundancy into your plans. Never bet everything on one outcome. "
            "Proper preparation for improbable events is essential.",
            ["investing", "risk_management"],
            ["Inversion", "Redundancy"],
        ),
        (
            "Second-Order Thinking",
            "Almost everyone focuses on first-order effects and ignores second and third-order effects. "
            "You have to think about the effects of the effects. What happens next? And what happens after that? "
            "The world is not static. Your actions have ripple effects. Think through the consequences of consequences.",
            ["thinking", "strategy"],
            ["Inversion", "Feedback Loops"],
        ),
        (
            "Opportunity Cost",
            "Intelligent people make decisions based on opportunity costs. Every dollar spent or hour used has an alternative. "
            "What are you NOT doing when you choose to do this? The cost of a thing is what you give up to get it. "
            "Always ask: What's the next best alternative?",
            ["economics", "decision_making"],
            ["Comparative Advantage", "Trade-offs"],
        ),
    ]

    return [
        MungerWisdom(
            category=WisdomCategory.MENTAL_MODEL,
            title=f"Mental Model: {name}",
            content=description,
            source="Charlie Munger - Mental Models Framework",
            tags=tags,
            related_models=related,
        )
        for name, description, tags, related in models
    ]


def _get_principles() -> list[MungerWisdom]:
    """Get Munger's life principles."""
    principles = [
        (
            "Continuous Learning",
            "Go to bed smarter than when you woke up. Develop into a lifelong self-learner through voracious reading. "
            "The game of life is the game of everlasting learning. At least it is if you want to win. "
            "I constantly see people rise in life who are not the smartest but they are learning machines. "
            "They go to bed a little wiser each day.",
            ["learning", "self_improvement"],
        ),
        (
            "Intellectual Humility",
            "Acknowledging what you don't know is the dawning of wisdom. Knowing what you don't know is more useful than being brilliant. "
            "There's no shame in not knowing. The shame is in pretending to know. "
            "Develop the habit of ruthlessly examining your own thinking for errors.",
            ["wisdom", "thinking"],
        ),
        (
            "Patience and Discipline",
            "The big money is in the waiting. You need patience, discipline, and agility to seize opportunities when they're presented. "
            "Occasionally, do nothing. Wait for the fat pitch. Don't swing at every ball. "
            "Most gains come from waiting for a few obvious opportunities.",
            ["investing", "character"],
        ),
        (
            "Avoiding Stupidity",
            "It is remarkable how much long-term advantage people like us have gotten by trying to be consistently not stupid, "
            "instead of trying to be very intelligent. Avoid stupidity is an easier goal than being brilliant. "
            "If you just avoid the major mistakes, you'll do well.",
            ["wisdom", "risk_management"],
        ),
        (
            "Deserving What You Want",
            "The safest way to get what you want is to deserve what you want. Deliver to the world what you would buy if you were on the other end. "
            "Be reliable, be ethical, be hardworking. Success follows those who deserve it through their conduct.",
            ["character", "success"],
        ),
        (
            "Reading and Thinking",
            "In my whole life, I have known no wise people who didn't read all the time. "
            "You'd be amazed at how much Warren reads and how much I read. My children laugh at me. "
            "They think I'm a book with a couple of legs sticking out.",
            ["learning", "habits"],
        ),
    ]

    return [
        MungerWisdom(
            category=WisdomCategory.PRINCIPLE,
            title=f"Principle: {name}",
            content=description,
            source="Charlie Munger - Life Principles",
            tags=tags,
            related_models=[],
        )
        for name, description, tags in principles
    ]


def _get_speech_excerpts() -> list[MungerWisdom]:
    """Get excerpts from famous Munger speeches."""
    excerpts = [
        (
            "Psychology of Human Misjudgment",
            "I've long been intrigued by standard thinking errors. I started cataloguing psychological tendencies "
            "that cause problems in cognition. There are about 25 standard causes of human misjudgment. "
            "Understanding these tendencies is essential for good decision-making. They include: "
            "reward and punishment super-response, liking/loving tendency, disliking/hating tendency, "
            "doubt-avoidance tendency, inconsistency-avoidance tendency, and many more.",
            "Psychology of Human Misjudgment speech, 1995",
            ["psychology", "mental_models"],
        ),
        (
            "Elementary Worldly Wisdom",
            "What is elementary worldly wisdom? It's a latticework of mental models. "
            "You've got to hang your experience on a latticework of models in your head. "
            "The first rule is that you've got to have multiple models - because if you just have one or two, "
            "the nature of human psychology is such that you'll torture reality so that it fits your models. "
            "You must have the models across many disciplines.",
            "Elementary Worldly Wisdom speech, USC Business School, 1994",
            ["mental_models", "learning"],
        ),
        (
            "The Art of Stock Picking",
            "The model I like - to sort of simplify the notion of what goes on in a market for common stocks - "
            "is the pari-mutuel system at the racetrack. If you stop to think about it, a pari-mutuel system is a market. "
            "Everybody goes there and bets, and the odds change based on what's bet. That's what happens in the stock market.",
            "The Art of Stock Picking speech, 1994",
            ["investing", "mental_models"],
        ),
        (
            "Academic Economics",
            "I have a habit of citing examples like this but I think they're important. "
            "Academic economics has serious problems. Essentially, I find it's just plain wrong. "
            "They have a paradigm with utility maximizing rationality, but it's a gross oversimplification "
            "of reality and often leads to wrong conclusions.",
            "Academic Economics speech, UC Santa Barbara, 2003",
            ["economics", "thinking"],
        ),
    ]

    return [
        MungerWisdom(
            category=WisdomCategory.SPEECH_EXCERPT,
            title=f"Speech: {name}",
            content=description,
            source=source,
            tags=tags,
            related_models=[],
        )
        for name, description, source, tags in excerpts
    ]
