import langchain.agents
from typing import Optional


# 类似 console.dir()
# print(dir(langchain.agents))

def say_hi(name: Optional[str] = None):
    if name is not None:
        print(f"Hey {name}!")
    else:
        print("Hello World")

print(say_hi("czl"))