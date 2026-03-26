import random

TOPICS = [
    "quantum physics",
    "Roman history", 
    "CUDA kernel optimization",
    "Renaissance art",
    "machine learning inference",
]

STYLES = [
    "in an explanatory tone",
    "for advanced students",
    "with practical examples",
    "as a bullet-point list",
    "in conversational style",
]

TASKS = [
    "explain the concept",
    "summarize key points",
    "propose exercises",
    "discuss pros and cons",
    "create a tutorial",
]

LENGTHS = [
    "around 200 words",
    "around 200 words",
    "around 200 words",
    "around 200 words",
]

TEMPLATES = [
    "{task} about {topic} {style} {length}.",
    "Write a {style} explanation of how to {task} {topic} {length}.",
    "Generate {length} content {style} that covers {task} for {topic}.",
]


TOPICS = [
    "quantum physics",
    "Roman history", 
    "CUDA kernel optimization",
    "Renaissance art",
    "machine learning inference",
]

STYLES = [
    "in an explanatory tone",
    "for advanced students",
    "with practical examples",
    "as a bullet-point list",
    "in conversational style",
]

TASKS = [
    "explain the concept",
    "summarize key points",
    "propose exercises",
    "discuss pros and cons",
    "create a tutorial",
]

LENGTHS = [
    "around 200 words",
    "around 200 words",
    "around 200 words",
    "around 200 words",
]

TEMPLATES = [
    "{task} about {topic} {style} {length}.",
    "Write a {style} explanation of how to {task} {topic} {length}.",
    "Generate {length} content {style} that covers {task} for {topic}.",
]


def generate_prompts(seed: int = None, num_prompts: int = 10) -> dict[int, str]:
    prompts_dict = {}
    for i in range(num_prompts+1):
        if seed is not None:
            random.seed((seed + i) % (2**32))
        template = random.choice(TEMPLATES)
        prompt = template.format(
            task=random.choice(TASKS),
            topic=random.choice(TOPICS),
            style=random.choice(STYLES),
            length=random.choice(LENGTHS),
        )
        prompts_dict[i] = prompt
    return prompts_dict

if __name__ == "__main__":
    print(generate_prompts(num_prompts = 4))


#print(generate_prompts(num_prompts=1)[0])
