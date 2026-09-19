from dotenv import load_dotenv
from openai import OpenAI


def main() -> None:
    load_dotenv()
    client = OpenAI()
    response = client.responses.create(
        model="gpt-4o",
        input="Escreva uma história de ninar de uma frase sobre um unicórnio.",
    )
    print(response.output_text)


if __name__ == "__main__":
    main()
