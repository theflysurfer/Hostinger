"""
MemVid RAG - Streamlit UI for project management
"""
import streamlit as st
import requests
from datetime import datetime
import json

# Configuration
API_URL = "http://memvid-api:8503"  # Internal Docker network

st.set_page_config(
    page_title="MemVid RAG Manager",
    page_icon="🎥",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def format_date(date_str):
    """Format datetime string"""
    if not date_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return date_str


def api_request(method, endpoint, **kwargs):
    """Make API request"""
    url = f"{API_URL}{endpoint}"
    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None


# Sidebar navigation
st.sidebar.markdown("# 🎥 MemVid RAG")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "➕ Create Project", "📁 Manage Projects", "🔍 Search & Chat"]
)

# ============================================================================
# DASHBOARD PAGE
# ============================================================================

if page == "📊 Dashboard":
    st.markdown('<div class="main-header">📊 Dashboard</div>', unsafe_allow_html=True)

    # Get all projects
    projects = api_request("GET", "/projects")

    if projects:
        # Overall stats
        total_projects = len(projects)
        total_chunks = sum(p.get("total_chunks", 0) for p in projects)
        total_size = sum(p.get("video_size_mb", 0) for p in projects)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Projects", total_projects)
        with col2:
            st.metric("Total Chunks", f"{total_chunks:,}")
        with col3:
            st.metric("Total Storage", f"{total_size:.2f} MB")

        st.markdown("---")

        # Projects list
        st.subheader("Projects")

        for project in projects:
            with st.expander(f"📁 {project['name']}", expanded=False):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**ID:** `{project['id']}`")
                    st.write(f"**Description:** {project.get('description', 'N/A')}")
                    st.write(f"**Tags:** {', '.join(project.get('tags', []))}")

                with col2:
                    st.write(f"**Chunks:** {project.get('total_chunks', 0)}")
                    st.write(f"**Size:** {project.get('video_size_mb', 0):.2f} MB")
                    st.write(f"**Files:** {project.get('files_count', 0)}")
                    st.write(f"**Updated:** {format_date(project.get('updated_at'))}")

    else:
        st.info("No projects found. Create your first project!")

# ============================================================================
# CREATE PROJECT PAGE
# ============================================================================

elif page == "➕ Create Project":
    st.markdown('<div class="main-header">➕ Create New Project</div>', unsafe_allow_html=True)

    with st.form("create_project"):
        name = st.text_input("Project Name *", placeholder="My RAG Project")
        description = st.text_area("Description", placeholder="Description of this project...")
        tags_input = st.text_input("Tags (comma-separated)", placeholder="documentation, python, ai")

        st.markdown("### Configuration")
        col1, col2 = st.columns(2)
        with col1:
            chunk_size = st.number_input("Chunk Size", min_value=128, max_value=4096, value=512)
        with col2:
            chunk_overlap = st.number_input("Chunk Overlap", min_value=0, max_value=512, value=64)

        submit = st.form_submit_button("Create Project", type="primary")

        if submit:
            if not name:
                st.error("Project name is required!")
            else:
                tags = [t.strip() for t in tags_input.split(",") if t.strip()]

                payload = {
                    "name": name,
                    "description": description if description else None,
                    "tags": tags,
                    "config": {
                        "chunk_size": chunk_size,
                        "chunk_overlap": chunk_overlap
                    }
                }

                result = api_request("POST", "/projects", json=payload)

                if result:
                    st.success(f"✅ Project '{name}' created successfully!")
                    st.json(result)
                    st.balloons()

# ============================================================================
# MANAGE PROJECTS PAGE
# ============================================================================

elif page == "📁 Manage Projects":
    st.markdown('<div class="main-header">📁 Manage Projects</div>', unsafe_allow_html=True)

    # Get all projects
    projects = api_request("GET", "/projects")

    if not projects:
        st.info("No projects found. Create your first project!")
    else:
        # Project selector
        project_options = {p["name"]: p for p in projects}
        selected_name = st.selectbox("Select Project", list(project_options.keys()))
        project = project_options[selected_name]

        st.markdown("---")

        # Project details
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader(f"📁 {project['name']}")
            st.write(f"**Description:** {project.get('description', 'N/A')}")
            st.write(f"**Tags:** {', '.join(project.get('tags', []))}")
            st.write(f"**ID:** `{project['id']}`")

        with col2:
            st.metric("Chunks", project.get('total_chunks', 0))
            st.metric("Size", f"{project.get('video_size_mb', 0):.2f} MB")
            st.metric("Files", project.get('files_count', 0))

        st.markdown("---")

        # Tabs for different actions
        tab1, tab2, tab3, tab4 = st.tabs(["📄 Index Text", "📤 Upload File", "📂 Index Folder", "⚙️ Settings"])

        # TAB 1: Index Text
        with tab1:
            st.subheader("Index Text")

            with st.form("index_text"):
                text_input = st.text_area(
                    "Enter text to index",
                    height=200,
                    placeholder="Paste your text here..."
                )

                submit_text = st.form_submit_button("Index Text", type="primary")

                if submit_text:
                    if not text_input:
                        st.error("Please enter some text!")
                    else:
                        with st.spinner("Indexing..."):
                            result = api_request(
                                "POST",
                                f"/projects/{project['id']}/index/text",
                                json={"text": text_input, "metadata": {}}
                            )

                            if result:
                                st.success("✅ Text indexed successfully!")
                                st.json(result)

        # TAB 2: Upload File
        with tab2:
            st.subheader("Upload File")

            uploaded_file = st.file_uploader(
                "Choose a file",
                type=["txt", "md", "pdf"],
                help="Supported formats: TXT, MD, PDF"
            )

            col1, col2 = st.columns(2)
            with col1:
                custom_chunk = st.checkbox("Use custom chunk size")
                if custom_chunk:
                    chunk_size_upload = st.number_input("Chunk Size", min_value=128, max_value=4096, value=512, key="upload_chunk")
            with col2:
                if custom_chunk:
                    overlap_upload = st.number_input("Chunk Overlap", min_value=0, max_value=512, value=64, key="upload_overlap")

            if uploaded_file is not None:
                if st.button("Index File", type="primary"):
                    with st.spinner(f"Indexing {uploaded_file.name}..."):
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                        params = {}
                        if custom_chunk:
                            params["chunk_size"] = chunk_size_upload
                            params["overlap"] = overlap_upload

                        result = api_request(
                            "POST",
                            f"/projects/{project['id']}/index/upload",
                            files=files,
                            params=params
                        )

                        if result:
                            st.success(f"✅ File '{uploaded_file.name}' indexed successfully!")
                            st.json(result)

        # TAB 3: Index Folder
        with tab3:
            st.subheader("Index Folder")

            st.info("⚠️ Note: Folder indexing requires the folder to be accessible from the Docker container.")

            with st.form("index_folder"):
                folder_path = st.text_input(
                    "Folder Path",
                    placeholder="/path/to/folder",
                    help="Absolute path to the folder"
                )

                col1, col2 = st.columns(2)
                with col1:
                    recursive = st.checkbox("Recursive scan", value=True)
                    extensions = st.multiselect(
                        "File Extensions",
                        [".txt", ".md", ".pdf", ".html", ".htm"],
                        default=[".txt", ".md", ".pdf"]
                    )
                with col2:
                    folder_custom_chunk = st.checkbox("Use custom chunk size", key="folder_chunk")
                    if folder_custom_chunk:
                        folder_chunk_size = st.number_input("Chunk Size", min_value=128, max_value=4096, value=512, key="folder_chunk_size")
                        folder_overlap = st.number_input("Chunk Overlap", min_value=0, max_value=512, value=64, key="folder_overlap")

                submit_folder = st.form_submit_button("Index Folder", type="primary")

                if submit_folder:
                    if not folder_path:
                        st.error("Please enter a folder path!")
                    else:
                        with st.spinner("Indexing folder..."):
                            payload = {
                                "folder_path": folder_path,
                                "recursive": recursive,
                                "file_extensions": extensions
                            }
                            if folder_custom_chunk:
                                payload["chunk_size"] = folder_chunk_size
                                payload["chunk_overlap"] = folder_overlap

                            result = api_request(
                                "POST",
                                f"/projects/{project['id']}/index/folder",
                                json=payload
                            )

                            if result:
                                st.success("✅ Folder indexed successfully!")
                                st.json(result)

        # TAB 4: Settings
        with tab4:
            st.subheader("Project Settings")

            # Update project
            with st.form("update_project"):
                new_name = st.text_input("Name", value=project["name"])
                new_description = st.text_area("Description", value=project.get("description", ""))
                new_tags = st.text_input("Tags (comma-separated)", value=", ".join(project.get("tags", [])))

                update_btn = st.form_submit_button("Update Project")

                if update_btn:
                    tags = [t.strip() for t in new_tags.split(",") if t.strip()]
                    payload = {
                        "name": new_name,
                        "description": new_description,
                        "tags": tags
                    }

                    result = api_request(
                        "PUT",
                        f"/projects/{project['id']}",
                        json=payload
                    )

                    if result:
                        st.success("✅ Project updated!")
                        st.rerun()

            st.markdown("---")

            # Danger zone
            st.markdown("### ⚠️ Danger Zone")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("🗑️ Reset Memory", help="Delete all indexed data (keeps project)"):
                    result = api_request("DELETE", f"/projects/{project['id']}/reset")
                    if result:
                        st.success("✅ Memory reset!")
                        st.rerun()

            with col2:
                if st.button("❌ Delete Project", help="Delete project and all data"):
                    result = api_request("DELETE", f"/projects/{project['id']}")
                    if result:
                        st.success("✅ Project deleted!")
                        st.rerun()

# ============================================================================
# SEARCH & CHAT PAGE
# ============================================================================

elif page == "🔍 Search & Chat":
    st.markdown('<div class="main-header">🔍 Search & Chat</div>', unsafe_allow_html=True)

    # Get all projects
    projects = api_request("GET", "/projects")

    if not projects:
        st.info("No projects found. Create your first project!")
    else:
        # Project selector
        project_options = {p["name"]: p for p in projects}
        selected_name = st.selectbox("Select Project", list(project_options.keys()))
        project = project_options[selected_name]

        # Check if project is indexed
        if project.get("total_chunks", 0) == 0:
            st.warning(f"⚠️ Project '{project['name']}' has no indexed data yet. Please index some content first.")
        else:
            st.success(f"✅ Project has {project.get('total_chunks', 0)} chunks indexed")

            # Tabs for search and chat
            tab1, tab2 = st.tabs(["🔍 Search", "💬 Chat"])

            # TAB 1: Search
            with tab1:
                st.subheader("Semantic Search")

                query = st.text_input("Search Query", placeholder="Enter your search query...")
                top_k = st.slider("Number of results", min_value=1, max_value=20, value=5)

                if st.button("Search", type="primary"):
                    if not query:
                        st.error("Please enter a search query!")
                    else:
                        with st.spinner("Searching..."):
                            result = api_request(
                                "POST",
                                f"/projects/{project['id']}/search",
                                json={"query": query, "top_k": top_k}
                            )

                            if result:
                                st.success(f"Found {len(result)} results")

                                for i, r in enumerate(result, 1):
                                    with st.expander(f"Result {i} (Score: {r['score']:.2f})", expanded=i<=3):
                                        st.write(r["text"])
                                        if r.get("metadata"):
                                            st.json(r["metadata"])

            # TAB 2: Chat
            with tab2:
                st.subheader("Chat with RAG")

                chat_query = st.text_area("Your Question", placeholder="Ask a question about your indexed content...")

                col1, col2, col3 = st.columns(3)
                with col1:
                    chat_top_k = st.number_input("Context Chunks", min_value=1, max_value=10, value=3)
                with col2:
                    ollama_model = st.selectbox("Model", ["qwen2.5:14b", "mistral:7b", "llama3.2:1b"])
                with col3:
                    ollama_url = st.text_input("Ollama URL", value="http://69.62.108.82:11434")

                if st.button("Ask", type="primary"):
                    if not chat_query:
                        st.error("Please enter a question!")
                    else:
                        with st.spinner("Thinking..."):
                            result = api_request(
                                "POST",
                                f"/projects/{project['id']}/chat",
                                json={
                                    "query": chat_query,
                                    "top_k": chat_top_k,
                                    "model": "ollama",
                                    "ollama_model": ollama_model,
                                    "ollama_base_url": ollama_url
                                }
                            )

                            if result:
                                st.markdown("### 💡 Answer")
                                st.write(result["answer"])

                                st.markdown("---")
                                st.markdown("### 📚 Sources")
                                st.write(f"Used {result['context_chunks']} context chunks")

                                for i, source in enumerate(result.get("sources", []), 1):
                                    with st.expander(f"Source {i}", expanded=False):
                                        st.write(source["text"])

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 System Info")
try:
    health = api_request("GET", "/health")
    if health:
        st.sidebar.success("✅ API Connected")
except:
    st.sidebar.error("❌ API Disconnected")

st.sidebar.markdown("---")
st.sidebar.caption("MemVid RAG v2.0 | Multi-project RAG system")
