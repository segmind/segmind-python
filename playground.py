import contextlib
import io
from pathlib import Path
from typing import Any

import streamlit as st

from segmind import SegmindClient

st.set_page_config(page_title="Segmind SDK Playground", layout="wide")
st.title("Segmind SDK Playground")


def get_client() -> SegmindClient:
    api_key = st.sidebar.text_input("API Key", type="password")
    base_url = st.sidebar.text_input("Base URL", value="https://api.segmind.com/v1")
    timeout = st.sidebar.number_input("Timeout (s)", min_value=1.0, value=30.0, step=1.0)

    if api_key:
        client = SegmindClient(api_key=api_key, base_url=base_url, timeout=timeout)
    else:
        client = SegmindClient(base_url=base_url, timeout=timeout)
    return client


client = get_client()

section = st.sidebar.selectbox(
    "Section",
    [
        "Models",
        "Generations",
        "Files",
        "Webhooks",
        "Finetune",
        "Run (Inference)",
    ],
)


def render_response(resp: Any) -> None:
    st.subheader("Response")
    st.json(resp)


if section == "Models":
    st.header("Models.list")
    if st.button("List Models"):
        with st.spinner("Fetching models..."):
            render_response(client.models.list())

elif section == "Generations":
    st.header("Generations")
    tab1, tab2 = st.tabs(["List", "Recent"])
    with tab1:
        page = st.number_input("page", min_value=1, value=1, step=1)
        model_name = st.text_input("model_name", value="")
        start_date = st.text_input("start_date (YYYY-MM-DD)", value="")
        end_date = st.text_input("end_date (YYYY-MM-DD)", value="")
        if st.button("Get Generations"):
            params: dict[str, Any] = {"page": int(page)}
            if model_name:
                params["model_name"] = model_name
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            with st.spinner("Fetching generations..."):
                render_response(client.generations.list(**params))

    with tab2:
        model_name_recent = st.text_input("model_name", key="recent_model_name")
        if st.button("Get Recent Generations"):
            with st.spinner("Fetching recent generations..."):
                render_response(client.generations.recent(model_name_recent))

elif section == "Files":
    st.header("Files.upload")
    uploaded = st.file_uploader("Upload media (image/audio/video)")
    if uploaded and st.button("Upload"):
        # Persist temporary file to disk for SDK method
        tmp_path = Path(st.secrets.get("tmp_dir", ".")) / uploaded.name
        tmp_bytes = uploaded.read()
        tmp_path.write_bytes(tmp_bytes)
        try:
            with st.spinner("Uploading..."):
                render_response(client.files.upload(str(tmp_path)))
        finally:
            with contextlib.suppress(Exception):
                tmp_path.unlink(missing_ok=True)


elif section == "Webhooks":
    st.header("Webhooks")
    tab_get, tab_add, tab_update, tab_delete, tab_logs = st.tabs([
        "Get",
        "Add",
        "Update",
        "Delete",
        "Logs",
    ])

    with tab_get:
        if st.button("Get Webhooks"):
            with st.spinner("Fetching webhooks..."):
                render_response(client.webhooks.get())

    with tab_add:
        url = st.text_input("webhook_url", key="add_url")
        event_types = st.text_input("event types (comma separated)", value="PIXELFLOW")
        if st.button("Add Webhook"):
            with st.spinner("Adding webhook..."):
                render_response(
                    client.webhooks.add(
                        url, [e.strip() for e in event_types.split(",") if e.strip()]
                    )
                )

    with tab_update:
        webhook_id = st.text_input("webhook_id", key="update_id")
        url_u = st.text_input("webhook_url", key="update_url")
        event_types_u = st.text_input(
            "event types (comma separated)", value="PIXELFLOW", key="update_types"
        )
        if st.button("Update Webhook"):
            with st.spinner("Updating webhook..."):
                render_response(
                    client.webhooks.update(
                        webhook_id,
                        url_u,
                        [e.strip() for e in event_types_u.split(",") if e.strip()],
                    )
                )

    with tab_delete:
        webhook_id_del = st.text_input("webhook_id", key="delete_id")
        if st.button("Delete Webhook"):
            with st.spinner("Deleting webhook..."):
                render_response(client.webhooks.delete(webhook_id_del))

    with tab_logs:
        webhook_id_logs = st.text_input("webhook_id", key="logs_id")
        if st.button("Get Logs"):
            with st.spinner("Fetching logs..."):
                render_response(client.webhooks.logs(webhook_id_logs))

elif section == "Finetune":
    st.header("Finetune")
    tab_presign, tab_submit, tab_details, tab_list, tab_access, tab_download = st.tabs([
        "Upload Presigned URL",
        "Submit",
        "Details",
        "List",
        "Access Update",
        "File Download",
    ])

    with tab_presign:
        fname = st.text_input("zip name (e.g., dataset.zip)")
        if st.button("Get Presigned URL"):
            with st.spinner("Requesting presigned URL..."):
                render_response(client.finetune.upload_presigned_url(name=fname))

    with tab_submit:
        name = st.text_input("name", value="flux-job-1")
        data_source_path = st.text_input("data_source_path (public zip or Segmind s3_url)")
        instance_prompt = st.text_input("instance_prompt", value="1MAN, running in brown suit")
        trigger_word = st.text_input("trigger_word", value="1MAN")
        base_model = st.selectbox("base_model", ["FLUX"], index=0)
        train_type = st.selectbox("train_type", ["LORA"], index=0)
        machine_type = st.selectbox(
            "machine_type", ["NVIDIA_A100_40GB", "NVIDIA_H100", "NVIDIA_L40S"], index=0
        )
        theme = st.text_input("theme", value="FLUX")
        segmind_public = st.checkbox("segmind_public", value=False)
        steps = st.number_input("steps", min_value=1, value=1000, step=10)
        batch_size = st.number_input("batch_size", min_value=1, value=2, step=1)
        learning_rate = st.number_input(
            "learning_rate", min_value=1e-6, value=4e-4, step=1e-5, format="%f"
        )
        if st.button("Submit Fine-tune"):
            with st.spinner("Submitting fine-tune request..."):
                payload = {
                    "steps": int(steps),
                    "batch_size": int(batch_size),
                    "learning_rate": float(learning_rate),
                }
                render_response(
                    client.finetune.submit(
                        name=name,
                        data_source_path=data_source_path,
                        instance_prompt=instance_prompt,
                        trigger_word=trigger_word,
                        base_model=base_model,
                        train_type=train_type,
                        machine_type=machine_type,
                        theme=theme,
                        segmind_public=segmind_public,
                        advance_parameters=payload,
                    )
                )

    with tab_details:
        request_id = st.text_input("request_id", key="ft_details")
        if st.button("Get Details"):
            with st.spinner("Fetching details..."):
                render_response(client.finetune.details(request_id))

    with tab_list:
        if st.button("List Fine-tunes"):
            with st.spinner("Listing..."):
                render_response(client.finetune.list())

    with tab_access:
        request_id_acc = st.text_input("request_id", key="ft_access")
        segmind_public_acc = st.checkbox("segmind_public", value=True, key="ft_access_cb")
        if st.button("Update Access"):
            with st.spinner("Updating access..."):
                render_response(client.finetune.access_update(request_id_acc, segmind_public_acc))

    with tab_download:
        cloud_storage_url = st.text_input("cloud_storage_url", key="ft_download")
        if st.button("Get Download URL"):
            with st.spinner("Generating download URL..."):
                url = client.finetune.file_download(cloud_storage_url)
                st.code(url)

elif section == "Run (Inference)":
    st.header("client.run (Model Inference)")
    slug = st.text_input("Model slug", value="seedream-v3-text-to-image")
    prompt = st.text_input("prompt", value="A beautiful sunset over mountains")
    aspect_ratio = st.text_input("aspect_ratio", value="16:9")
    if st.button("Run"):
        with st.spinner("Running model..."):
            resp = client.run(slug, prompt=prompt, aspect_ratio=aspect_ratio)
            # Try display as image; otherwise show text/json
            try:
                st.image(io.BytesIO(resp.content))
            except Exception:
                try:
                    st.json(resp.json())
                except Exception:
                    st.write(resp.text)
