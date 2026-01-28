import os
import re
import pandas as pd

# Live AI is optional (only used if credits + key work)
try:
    from openai import OpenAI
    _HAS_OPENAI = True
except Exception:
    _HAS_OPENAI = False


def dataset_context(df: pd.DataFrame, max_rows: int = 8) -> str:
    lines = []
    lines.append(f"Dataset: {df.shape[0]} rows x {df.shape[1]} cols")
    lines.append("Columns (name: dtype):")
    for c in df.columns:
        lines.append(f"- {c}: {df[c].dtype}")

    lines.append("\nSample rows:")
    lines.append(df.head(max_rows).to_string(index=False))

    num_cols = df.select_dtypes(include="number").columns.tolist()
    if num_cols:
        lines.append("\nNumeric summary (describe):")
        lines.append(df[num_cols].describe().round(2).to_string())

    return "\n".join(lines)


def _demo_answer(question: str, df: pd.DataFrame) -> str:
    """Offline/demo analyst-like response using real stats (no API)."""
    q = (question or "").strip().lower()

    if df is None or df.empty:
        return "Dataset is empty. Please upload a CSV first."

    # Basic stats
    rows, cols = df.shape
    missing_cells = int(df.isna().sum().sum())
    dup_rows = int(df.duplicated().sum())

    num_cols = df.select_dtypes(include="number").columns.tolist()
    obj_cols = df.select_dtypes(include=["object"]).columns.tolist()

    # Try to pick useful columns
    def pick_col(keys, cols_list):
        for k in keys:
            for c in cols_list:
                if k in c.lower():
                    return c
        return None

    metric_col = pick_col(["sales", "revenue", "profit", "amount"], num_cols) or (
        num_cols[0] if num_cols else None
    )
    cat_col = pick_col(
        ["category", "segment", "state", "city", "region", "product"], obj_cols
    ) or (obj_cols[0] if obj_cols else None)

    # Common responses
    if any(
        w in q
        for w in ["summary", "summarize", "overview", "describe", "what is this data"]
    ):
        parts = [
            "### ✅ Demo Mode: Dataset Summary (offline)\n",
            f"- **Rows:** {rows}",
            f"- **Columns:** {cols}",
            f"- **Missing cells:** {missing_cells}",
            f"- **Duplicate rows:** {dup_rows}",
            "",
            (
                f"**Numeric columns ({len(num_cols)}):** {', '.join(num_cols[:10])}"
                f"{' ...' if len(num_cols) > 10 else ''}"
                if num_cols
                else "**Numeric columns:** none"
            ),
            (
                f"**Text/Categorical columns ({len(obj_cols)}):** {', '.join(obj_cols[:10])}"
                f"{' ...' if len(obj_cols) > 10 else ''}"
                if obj_cols
                else "**Text/Categorical columns:** none"
            ),
        ]

        if metric_col:
            parts.append(f"\n**Main metric guess:** `{metric_col}`")
            # ✅ tiny patch: :,.2f (not : ,2f)
            parts.append(
                f"- Total {metric_col}: `{df[metric_col].sum():,.2f}`")
            parts.append(
                f"- Average {metric_col}: `{df[metric_col].mean():,.2f}`")

        return "\n".join(parts)

    if any(w in q for w in ["missing", "null", "na", "empty"]):
        top_missing = df.isna().sum().sort_values(ascending=False).head(10)
        top_missing = top_missing[top_missing > 0]
        if top_missing.empty:
            return "### ✅ Demo Mode\nNo missing values found ✅"

        lines = ["### ✅ Demo Mode: Missing Values (top columns)"]
        for col, cnt in top_missing.items():
            lines.append(f"- `{col}`: {int(cnt)}")
        return "\n".join(lines)

    if any(w in q for w in ["duplicate", "duplicates"]):
        return (
            "### ✅ Demo Mode: Duplicates\n"
            f"- Duplicate rows found: **{dup_rows}**\n"
            "Tip: You can remove duplicates using the cleaning step."
        )

    if any(
        w in q
        for w in ["top", "best", "highest", "most", "category", "segment", "region", "state", "city"]
    ):
        if not cat_col:
            return (
                "### ✅ Demo Mode\n"
                "I couldn't find a categorical column to rank. "
                "Try uploading a dataset with category-like columns."
            )

        vc = df[cat_col].astype(str).value_counts().head(10)
        lines = [f"### ✅ Demo Mode: Top values for `{cat_col}` (by count)"]
        for k, v in vc.items():
            lines.append(f"- **{k}**: {int(v)}")

        if metric_col and metric_col in df.columns:
            grp = (
                df.groupby(cat_col)[metric_col]
                .sum()
                .sort_values(ascending=False)
                .head(10)
            )
            lines.append(
                f"\n### 🔥 `{metric_col}` by `{cat_col}` (sum, top 10)")
            for k, v in grp.items():
                # ✅ tiny patch: :,.2f (not : ,2f)
                lines.append(f"- **{k}**: {float(v):,.2f}")

        return "\n".join(lines)

    # Default: give useful analyst guidance
    msg = [
        "### ✅ Demo Mode (offline)\n",
        "I can answer using real stats even without API credits.",
        "Try asking:",
        "- `Summarize this dataset`",
        "- `Show missing values`",
        "- `Top categories and metric leaders`",
    ]
    if metric_col:
        msg.append(
            f"- `What drives {metric_col}?` (I’ll show quick breakdowns)")
    return "\n".join(msg)


def ask_ai(question: str, df: pd.DataFrame, chat_history: list) -> str:
    """
    AUTO mode:
    - Try Live AI if possible
    - If it fails (0 credits / auth / network), fallback to Demo Mode
    """
    # Always provide a working answer
    demo = _demo_answer(question, df)

    # If no OpenAI package or no key, just demo
    api_key = os.getenv("OPENAI_API_KEY", "")
    if (not _HAS_OPENAI) or (not api_key):
        return demo

    # Try live AI; if anything fails, fallback to demo
    try:
        client = OpenAI(api_key=api_key)

        context = dataset_context(df)
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a data analyst assistant. "
                    "Answer using the dataset context provided. "
                    "Be concise and use bullet points when helpful."
                ),
            },
            {"role": "user", "content": f"DATASET CONTEXT:\n{context}"},
        ]

        for m in (chat_history or [])[-8:]:
            # keep only valid roles
            if (
                isinstance(m, dict)
                and m.get("role") in ("user", "assistant")
                and "content" in m
            ):
                messages.append(
                    {"role": m["role"], "content": str(m["content"])})

        messages.append({"role": "user", "content": question})

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,
        )
        return completion.choices[0].message.content

    except Exception:
        # Credits/auth errors end up here → demo mode saves the day
        return demo
