"""Uses Groq's free API (no credit card needed) for answer generation.
Groq exposes an OpenAI-compatible endpoint, so we just point the OpenAI
client at Groq's base_url instead of OpenAI's."""
from openai import OpenAI
from app.config import settings

client = OpenAI(api_key=settings.groq_api_key, base_url="https://api.groq.com/openai/v1")

SYSTEM_PROMPT = """You are an assistant that answers questions about Indian Railways
parcel, luggage, freight, and policy documents using ONLY the context provided below.

Rules:
- If a "STRUCTURED RATE TABLE MATCHES" entry is present, it is an EXACT, VERIFIED
  lookup result. State the rate directly.
- If a "RELEVANT DOCUMENT TEXT" section is present and non-empty, you MUST use it
  to answer the question as best you can, even if the match is partial or the
  wording doesn't exactly match the question. Summarize what the text says that
  relates to the question. Do NOT refuse just because the answer isn't a perfect
  or complete match — extract and explain whatever relevant information exists.
- Only respond "I cannot confirm this from the available documents" if the context
  is completely empty, or is about a totally unrelated topic with zero connection
  to the question.
- Never invent a rate, distance slab, or rule that isn't in the context.
- Keep answers concise. Cite the source document/page when possible.
"""


def build_context_string(retrieval_result: dict) -> str:
    parts = []
    if retrieval_result["table_rows"]:
        parts.append("STRUCTURED RATE TABLE MATCHES:")
        for row in retrieval_result["table_rows"]:
            parts.append(
                f"- {row['scale']} ({row['category']}): distance {row['distance_range_km']} km, "
                f"weight up to {row['weight_slab_kg']} kg -> Rs. {row['rate_rs']} "
                f"(page {row['page_number']})"
            )
    if retrieval_result["semantic_chunks"]:
        parts.append("\nRELEVANT DOCUMENT TEXT:")
        for chunk in retrieval_result["semantic_chunks"]:
            meta = chunk["metadata"]
            parts.append(f"- [{meta['filename']}, page {meta['page_number']}]: {chunk['text']}")
    return "\n".join(parts) if parts else "No relevant context found in the knowledge base."


def generate_answer(user_query: str, retrieval_result: dict) -> dict:
    context = build_context_string(retrieval_result)

    # Deterministic shortcut: if this was a pure table lookup with exact match(es),
    # skip the LLM entirely. The small free model tends to second-guess correct
    # numeric matches, so trust the SQL lookup instead of asking it to "confirm."
    if retrieval_result["mode"] == "table" and retrieval_result["table_rows"]:
        rows = retrieval_result["table_rows"]
        if len(rows) == 1:
            r = rows[0]
            answer = (
                f"The rate is Rs. {r['rate_rs']} for {r['scale']} ({r['category']}), "
                f"distance {r['distance_range_km']} km, weight up to {r['weight_slab_kg']} kg "
                f"(source: page {r['page_number']})."
            )
        else:
            lines = [
                f"- {r['scale']} ({r['category']}): {r['distance_range_km']} km, "
                f"up to {r['weight_slab_kg']} kg -> Rs. {r['rate_rs']} (page {r['page_number']})"
                for r in rows
            ]
            answer = "Found multiple matching rates:\n" + "\n".join(lines)
        return {"answer": answer, "context_used": context, "retrieval_mode": retrieval_result["mode"]}

    response = client.chat.completions.create(
        model=settings.generation_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"CONTEXT:\n{context}\n\nQUESTION: {user_query}"},
        ],
        temperature=0.1,
    )
    return {
        "answer": response.choices[0].message.content,
        "context_used": context,
        "retrieval_mode": retrieval_result["mode"],
    }