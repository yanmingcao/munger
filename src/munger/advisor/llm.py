"""LLM integration for advice generation."""

from collections.abc import AsyncIterator, Iterator
from typing import Any

from munger.core.config import settings


def get_openai_client():
    """Get OpenAI client."""
    from openai import OpenAI

    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY not set. Set MUNGER_OPENAI_API_KEY environment variable.")

    return OpenAI(api_key=settings.openai_api_key)


def get_anthropic_client():
    """Get Anthropic client."""
    from anthropic import Anthropic

    if not settings.anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY not set. Set MUNGER_ANTHROPIC_API_KEY environment variable.")

    return Anthropic(api_key=settings.anthropic_api_key)


def get_kimi_client():
    """Get Kimi (Moonshot AI) client."""
    from openai import OpenAI

    if not settings.kimi_api_key:
        raise ValueError("KIMI_API_KEY not set. Set MUNGER_KIMI_API_KEY environment variable.")

    return OpenAI(
        api_key=settings.kimi_api_key,
        base_url="https://api.moonshot.cn/v1"
    )


def get_siliconflow_client():
    """Get SiliconFlow client."""
    from openai import OpenAI

    if not settings.siliconflow_api_key:
        raise ValueError("SILICONFLOW_API_KEY not set. Set MUNGER_SILICONFLOW_API_KEY environment variable.")

    return OpenAI(
        api_key=settings.siliconflow_api_key,
        base_url="https://api.siliconflow.cn/v1"
    )


def generate_response(
    messages: list[dict[str, str]],
    stream: bool = False,
) -> str | Iterator[str]:
    """Generate a response using the configured LLM provider."""
    if settings.llm_provider == "openai":
        return _generate_openai(messages, stream)
    elif settings.llm_provider == "anthropic":
        return _generate_anthropic(messages, stream)
    elif settings.llm_provider == "kimi":
        return _generate_kimi(messages, stream)
    elif settings.llm_provider == "siliconflow":
        return _generate_siliconflow(messages, stream)
    else:
        raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")


def _generate_openai(
    messages: list[dict[str, str]],
    stream: bool = False,
) -> str | Iterator[str]:
    """Generate response using OpenAI."""
    client = get_openai_client()

    if stream:
        return _stream_openai(client, messages)
    else:
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,  # type: ignore
            temperature=0.7,
            max_tokens=2000,
        )
        return response.choices[0].message.content or ""


def _stream_openai(client: Any, messages: list[dict[str, str]]) -> Iterator[str]:
    """Stream response from OpenAI."""
    stream = client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,  # type: ignore
        temperature=0.7,
        max_tokens=2000,
        stream=True,
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def _generate_anthropic(
    messages: list[dict[str, str]],
    stream: bool = False,
) -> str | Iterator[str]:
    """Generate response using Anthropic."""
    client = get_anthropic_client()

    # Convert messages format for Anthropic
    system_message = ""
    anthropic_messages = []

    for msg in messages:
        if msg["role"] == "system":
            system_message += msg["content"] + "\n\n"
        else:
            anthropic_messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })

    if stream:
        return _stream_anthropic(client, system_message, anthropic_messages)
    else:
        response = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=2000,
            system=system_message.strip(),
            messages=anthropic_messages,
        )
        return response.content[0].text


def _stream_anthropic(
    client: Any,
    system: str,
    messages: list[dict[str, str]],
) -> Iterator[str]:
    """Stream response from Anthropic."""
    with client.messages.stream(
        model=settings.anthropic_model,
        max_tokens=2000,
        system=system,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            yield text


def _generate_kimi(
    messages: list[dict[str, str]],
    stream: bool = False,
) -> str | Iterator[str]:
    """Generate response using Kimi (Moonshot AI)."""
    client = get_kimi_client()

    if stream:
        return _stream_kimi(client, messages)
    else:
        response = client.chat.completions.create(
            model=settings.kimi_model,
            messages=messages,  # type: ignore
            temperature=0.7,
            max_tokens=2000,
        )
        return response.choices[0].message.content or ""


def _stream_kimi(client: Any, messages: list[dict[str, str]]) -> Iterator[str]:
    """Stream response from Kimi (Moonshot AI)."""
    stream = client.chat.completions.create(
        model=settings.kimi_model,
        messages=messages,  # type: ignore
        temperature=0.7,
        max_tokens=2000,
        stream=True,
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def _generate_siliconflow(
    messages: list[dict[str, str]],
    stream: bool = False,
) -> str | Iterator[str]:
    """Generate response using SiliconFlow."""
    client = get_siliconflow_client()

    if stream:
        return _stream_siliconflow(client, messages)
    else:
        response = client.chat.completions.create(
            model=settings.siliconflow_model,
            messages=messages,  # type: ignore
            temperature=0.7,
            max_tokens=2000,
        )
        return response.choices[0].message.content or ""


def _stream_siliconflow(client: Any, messages: list[dict[str, str]]) -> Iterator[str]:
    """Stream response from SiliconFlow."""
    stream = client.chat.completions.create(
        model=settings.siliconflow_model,
        messages=messages,  # type: ignore
        temperature=0.7,
        max_tokens=2000,
        stream=True,
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
