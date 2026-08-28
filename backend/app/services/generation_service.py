
import json
import os
from urllib import error, request


class GenerationError(Exception):
    pass


def generate_answer(
    prompt: str,
) -> str:
    base_url = os.getenv(
        "OLLAMA_BASE_URL",
        "http://127.0.0.1:11434",
    ).rstrip("/")

    model = os.getenv(
        "OLLAMA_MODEL",
        "llama3.2:3b",
    )

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
        },
    }

    data = json.dumps(
        payload
    ).encode("utf-8")

    http_request = request.Request(
        url=f"{base_url}/api/generate",
        data=data,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(
            http_request,
            timeout=120,
        ) as response:
            response_body = response.read()

    except error.HTTPError as exc:
        raise GenerationError(
            f"Ollama returned HTTP {exc.code}."
        ) from exc

    except error.URLError as exc:
        raise GenerationError(
            "Could not connect to Ollama."
        ) from exc

    except TimeoutError as exc:
        raise GenerationError(
            "Ollama request timed out."
        ) from exc

    try:
        result = json.loads(
            response_body.decode("utf-8")
        )
    except json.JSONDecodeError as exc:
        raise GenerationError(
            "Invalid response from Ollama."
        ) from exc

    answer = result.get(
        "response",
        "",
    ).strip()

    if not answer:
        raise GenerationError(
            "Ollama returned an empty answer."
        )

    return answer