# markdownlp: NLP Tools for Markdown

`markdownlp` is a Python-based collection of Natural Language Processing (NLP) tools designed to enhance your Markdown workflows. The primary tool currently offered is `md_auto_tags`, a powerful command-line utility that automatically extracts relevant keywords from your Markdown or HTML documents and adds them as tags to your Markdown file's YAML front matter.

## Part 1: General Audience

### What is `md_auto_tags`?

`md_auto_tags` intelligently analyzes the content of your documents to identify key topics and phrases. It then populates the `tags` metadata field in your Markdown files, which can be invaluable for content organization, search engine optimization (SEO), and integration with documentation systems like MkDocs.

Imagine you have a large collection of Markdown articles. Manually tagging each one can be tedious and inconsistent. `md_auto_tags` automates this process, ensuring your content is accurately and efficiently categorized.

### Who is it for?

This tool is particularly beneficial for:

*   **Technical Writers & Documentarians:** Especially those using MkDocs with the Material theme and its `tags` plugin, as `md_auto_tags` seamlessly integrates with this setup.
*   **Content Creators & Bloggers:** Anyone working with Markdown who wants to improve content discoverability and organization.
*   **Developers:** Who need to automate tagging for project documentation or knowledge bases.

### Why is it useful?

*   **Saves Time & Effort:** Automates the often laborious task of manual tagging.
*   **Improves Consistency:** Applies a systematic approach to keyword extraction, leading to more uniform tagging across documents.
*   **Enhances SEO:** By identifying and adding relevant keywords as tags, it can help search engines better understand and rank your content.
*   **Better Content Organization:** Makes it easier to categorize, find, and manage your Markdown files.
*   **MkDocs Integration:** Works exceptionally well with the MkDocs Material `tags` plugin, allowing for automatic population of the tags displayed on your site.
*   **Smart Extraction:** Uses sophisticated NLP techniques to identify meaningful keywords, not just common words.

### Installation

You can install `markdownlp` using pip.

**1. From PyPI (Recommended for most users):**

```bash
python3 -m pip install markdownlp
```
*(Note: As of the creation of this README, the package might not yet be on PyPI. The setup.py is configured for it, but the original README only listed GitHub installation.)*

**2. From GitHub (for the latest version):**

```bash
python3 -m pip install git+https://github.com/twardoch/markdownlp
```

**Dependencies:**

The tool relies on several Python libraries for its functionality, including `spacy`, `nltk`, `pke` (Python Keyword Extraction), `beautifulsoup4`, and `Markdown`. These will be installed automatically when you install `markdownlp`. For non-English language processing, you might need to download additional `spacy` language models (e.g., `python -m spacy download de_core_news_sm` for German).

### Basic Usage (Command-Line)

The `md_auto_tags` tool is the primary utility. Here's how to use it:

**1. Processing a single Markdown file:**

The tool will convert the Markdown to HTML on the fly, extract text, and then generate tags.

```bash
md_auto_tags "path/to/your/document.md"
```

**2. Processing a Markdown file with a corresponding HTML file:**

This is useful if your HTML generation process involves other tools or plugins (like in MkDocs) that modify or add content.

```bash
md_auto_tags "path/to/your/document.md" --html_path="path/to/corresponding/document.html"
```

**3. Processing a folder of Markdown files (recursive):**

The tool will search for `.md` files in the specified folder and its subfolders.

```bash
md_auto_tags "path/to/markdown_folder/"
```
If you also have a corresponding folder of HTML files (e.g., your MkDocs `site` directory):
```bash
md_auto_tags "path/to/markdown_folder/" --html_path="path/to/html_folder/"
```

**Commonly Used Options:**

*   `--selector="article"`: If processing HTML files (especially from MkDocs Material), this tells the tool to only analyze the content within the `<article>` tag, ignoring headers, footers, and navigation. Defaults to `"html"` (the whole document).
*   `--lang="en"`: Specifies the language of the content (e.g., `"de"` for German, `"fr"` for French). Defaults to `"en"`.
*   `--slug`: Converts tags to lowercase and replaces spaces with hyphens (e.g., "My Tag" becomes "my-tag").
*   `--prefix="#"`: Adds a prefix to each tag (e.g., with `--slug` and `--prefix="#"`, "My Tag" becomes "#my-tag").

You can also invoke the tool via `python3 -m markdownlp.md_auto_tags MD_PATH ...`.

### Programmatic Usage

While primarily a CLI tool, the core logic of `md_auto_tags` can be imported and used in your Python scripts.

```python
from markdownlp.md_auto_tags import TagDoc, TagExtractor, md_auto_tags, get_paths

# Option 1: Process a single file
md_file = "path/to/your/document.md"
html_file = "path/to/corresponding/document.html" # Optional, can be same as md_file

# Initialize TagDoc to load and parse the document
# This will read the Markdown file, its metadata, and the HTML (or generate it)
doc = TagDoc(md_path=md_file, html_path=html_file, selector="article")

# Initialize TagExtractor with desired settings
extractor = TagExtractor(
    lang="en",
    slug=True,
    prefix="#",
    boost_headings=True
)

# Load the document into the extractor
extractor.load(doc)

# Perform keyword extraction
extractor.extract()

# Store the extracted tags back into the document's metadata
extractor.store()

# Save the modified Markdown file
doc.save()
print(f"Tags for {md_file}: {doc.tags}")

# Option 2: Use the main function (similar to CLI)
# This is useful for processing multiple files or using the CLI argument parsing
# md_auto_tags(
# md_path="path/to/markdown_folder/",
# html_path="path/to/html_folder/", # Optional
# selector="article",
# boost_headings=True,
# lang="en",
# slug=True,
# prefix="#",
# verbose=True
# )

# To get a dictionary of Markdown paths to HTML paths:
# paths = get_paths("path/to/markdown_folder/", "path/to/html_folder/")
# for md_p, html_p in paths.items():
# print(f"MD: {md_p}, HTML: {html_p}")
```

**Key Classes:**

*   `TagDoc(md_path, html_path="", selector="html", tags_global_no=None)`: Handles loading the Markdown file, its metadata, and the corresponding HTML content (either by reading an HTML file or by converting the Markdown to HTML).
*   `TagExtractor(lang="en", slug=True, prefix="#", retag=False, auto_only=False, boost_headings=False, stop_words=[])`: Contains the NLP logic for extracting and scoring keywords from the text provided by `TagDoc`.

## Part 2: Technical Details

### How `md_auto_tags` Works

1.  **File Handling & Path Matching (`get_paths`):**
    *   If `MD_PATH` is a file, it's processed directly. If `html_path` is also a file, it's used as the HTML source. If `html_path` is not provided or is the same as `MD_PATH`, the Markdown content is converted to HTML.
    *   If `MD_PATH` is a directory, the tool recursively scans for `*.md` files.
    *   For each Markdown file found in a directory, it tries to find a corresponding HTML file in `html_path` (if provided as a directory). It attempts to match by replacing the Markdown source base path with the HTML source base path and looking for `file.html` or `file/index.html`. If no corresponding HTML file is found, the Markdown itself is used to generate HTML.

2.  **HTML Conversion & Parsing (`TagDoc`):**
    *   If an HTML file isn't provided or isn't found, the Markdown content is converted to HTML using the `markdown` library with several common extensions enabled (e.g., `full_yaml_metadata`, `admonition`, `toc`, `pymdownx.betterem`).
    *   The HTML (either provided or generated) is then parsed using `BeautifulSoup`.

3.  **Text Extraction (`TagDoc`, `html22text`):**
    *   The textual content is extracted from the parsed HTML using the `html22text` library.
    *   The `--selector` argument (e.g., `"article"`, `"main"`, default `"html"`) determines which part of the HTML DOM is considered for text extraction. This is crucial for excluding irrelevant content like navigation bars, sidebars, or footers.

4.  **Keyword Extraction (`TagExtractor`):**
    *   **NLP Libraries:** The tool leverages `spacy` for basic language processing and `pke` (Python Keyword Extraction) for its core keyword extraction algorithms. `nltk` is used as a fallback or for specific tasks like WordNet lookups if `pattern.en` (used by `pke` for lemmatization) is not available.
    *   **Models Employed:** It uses a combination of unsupervised keyword extraction models from `pke`:
        *   `TfIdf`: Term Frequency-Inverse Document Frequency.
        *   `TopicalPageRank`: A graph-based method that considers the topical relations between words.
        *   `KPMiner`: Keyword extraction based on keyphrase mining.
        *   `Kea`: (Though typically supervised, `pke` might use its unsupervised candidate selection aspects).
        Each model contributes candidates, and their scores are weighted and combined.
    *   **Boosting Headings:** If `--boost_headings` is enabled, text found within HTML heading tags (H1-H6) is given higher importance during the extraction process. Different heading levels get different boosts (e.g., H1 text is weighted more heavily than H2).
    *   **Candidate Selection & Weighting:** `pke` models select candidate keywords (sequences of one or more words, typically nouns and adjectives) and assign them weights based on statistical properties and graph-based measures.
    *   **Stop Word Removal:** Common words (stop words) for the specified language (e.g., "the", "a", "is" for English) are removed before analysis. Additional custom stop words can be provided via the `--stop_words` argument.
    *   **Scoring & Selection:** Tags from different models and boosted sections are aggregated. The final list of tags is determined by these aggregated scores, and the number of tags is heuristically determined based on the document length (longer documents get more tags).

5.  **Language Support:**
    *   Defaults to English (`"en"`).
    *   For other languages supported by `spacy` and `pke`, you need to:
        1.  Specify the language code with `--lang`.
        2.  Ensure the appropriate `spacy` language model is installed (e.g., `python3 -m spacy download de_core_news_sm` for German). The tool attempts to download `en_core_web_sm` on first run if not found but may require manual installation for other languages.

6.  **Tag Processing (`TagExtractor`):**
    *   **Singularization (English):** For English, attempts to convert plural nouns in tags to their singular form (e.g., "articles" becomes "article") if the singular form is a valid noun.
    *   **Slugification:** If `--slug` is used, tags are converted to lowercase, and spaces are replaced with hyphens (e.g., "Data Science" becomes "data-science").
    *   **Prefixing:** If `--prefix` is used, the specified prefix is added to each tag (e.g., `"#"` results in tags like `"#data-science"`).

7.  **Metadata Handling (`TagDoc`, `oyaml`):**
    *   The tool reads the YAML front matter of the Markdown file using `oyaml`.
    *   It respects several `tags-*` fields in your Markdown's front matter:
        *   `tags`: This is where the tool will write the list of generated tags. Existing tags may be overwritten unless they are also in `tags-yes`.
        *   `tags-yes`: A list of tags that will always be included in the final `tags` list, regardless of what the NLP models generate. These are given a very high score.
        *   `tags-no`: A list of tags that will be excluded from the generated `tags` list, even if the NLP models identify them. This overrides `tags-yes` if a tag is in both.
        *   `tags-global-no`: A space-separated list of tags (provided via CLI argument `--tags_global_no`) to exclude globally, in addition to `tags-no`.
        *   `tags-done: true`: If this is present and the `--retag` CLI flag is *not* set, the tool will skip processing this file. This prevents re-processing already tagged files. The tool sets `tags-done: true` after processing a file.
        *   `tags-auto: true`: If the `--auto_only` CLI flag is set, the tool will only process files that have `tags-auto: true` in their front matter. The tool writes this entry after it has processed a file (this behavior might be intended to mark files that are suitable for auto-tagging).
        *   `tags-none: true`: If this is present, the tool will not generate any tags for this file, effectively skipping the extraction process for it.
    *   After processing, the updated metadata (with the new `tags` list and `tags-done: true`) is written back to the Markdown file, preserving the rest of the front matter and the Markdown body.

### Command-Line Interface (CLI) - Detailed Arguments

The `md_auto_tags` tool is invoked as follows:
`md_auto_tags MD_PATH [OPTIONS]`
or
`python3 -m markdownlp.md_auto_tags MD_PATH [OPTIONS]`

*   `MD_PATH`: (Required) Path to the Markdown file or a folder containing Markdown files. If a folder, processing is recursive.
*   `--html_path=HTML_PATH`: Optional path to a corresponding HTML file or a folder containing HTML files. If `MD_PATH` is a folder, `HTML_PATH` should also be a folder with a similar structure. If not provided, HTML is generated from the Markdown.
*   `--selector="html"`: CSS selector used to extract text content from HTML. For MkDocs Material, `"article"` is recommended. Defaults to `"html"` (entire document).
*   `--boost_headings`: (Flag, boolean) If set, text within H1-H6 tags is considered more important during keyword extraction.
*   `--lang="en"`: Language code for the text (e.g., "en", "de", "es"). Defaults to "en". Requires appropriate spaCy models for non-English languages.
*   `--slug`: (Flag, boolean) If set, slugify tags (e.g., "My Topic" becomes "my-topic").
*   `--prefix=""`: String to prefix to each tag. Useful with `--slug`, e.g., `--prefix="#"`. Defaults to an empty string.
*   `--auto_only`: (Flag, boolean) If set, only process Markdown files that have `tags-auto: true` in their YAML front matter.
*   `--retag`: (Flag, boolean) If set, re-process Markdown files even if `tags-done: true` is present in their YAML front matter. By default, files with `tags-done: true` are skipped.
*   `--tags_global_no=""`: A space-separated string of tags to globally exclude from being generated. These are added to any file-specific `tags-no` lists.
*   `--stop_words=""`: A space-separated string of additional stop words to be ignored during NLP analysis, supplementing the default language stop word list.
*   `--verbose`: (Flag, boolean) If set, print detailed logging output during processing.

### Dependencies

Key libraries used by `markdownlp`:

*   **`Markdown`**: For converting Markdown text to HTML when an HTML source is not provided.
*   **`pymdown-extensions`**: Provides additional extensions for the `Markdown` library.
*   **`html22text` (custom fork `twardoch/html22text`)**: For converting HTML content to plain text, with options to specify selectors.
*   **`html5lib`**: An HTML parser used by BeautifulSoup.
*   **`beautifulsoup4`**: For parsing HTML documents.
*   **`fire`**: For quickly creating command-line interfaces from Python code.
*   **`nltk`**: Natural Language Toolkit, used for some NLP tasks like WordNet access.
*   **`spacy`**: Industrial-strength NLP library, used for tokenization, part-of-speech tagging, and language model loading.
*   **`pke` (Python Keyword Extraction, fork `boudinfl/pke`)**: The core library used for various keyword and keyphrase extraction algorithms.
*   **`python-slugify`**: For converting strings into URL-friendly slugs.
*   **`markdown-full-yaml-metadata`**: For parsing YAML front matter in Markdown files that spans multiple lines or has complex structures.
*   **`oyaml`**: A YAML library that preserves ordering and comments, used for reading and writing Markdown front matter.
*   **`pattern`**: (Indirect dependency via `pke` or used for singularization) For NLP tasks including morphology.

Refer to `requirements.txt` for specific versions and a complete list.

### Coding and Contribution Guidelines

*   **Project Structure:**
    *   `markdownlp/`: Contains the main Python module.
        *   `md_auto_tags.py`: Core logic for the `md_auto_tags` tool.
    *   `setup.py`: Standard Python package setup file.
    *   `requirements.txt`: Lists package dependencies.
    *   `README.md`: This file.
    *   `LICENSE`: Contains the MIT license.
    *   `VERSION.txt`: Currently seems to be a placeholder note rather than a version string. For actual versioning, `setup.py` has `version="1.0.0"`.
*   **Code Style:**
    *   The code generally follows PEP 8 guidelines but has some longer lines.
    *   Consider using a formatter like Black or Ruff for consistency.
*   **Dependencies:**
    *   Install dependencies using `pip install -r requirements.txt`.
    *   For development, you might want to install the package in editable mode: `pip install -e .`
*   **Running Tests:**
    *   Currently, there are no automated tests in the repository. Adding tests (e.g., using `pytest`) would be a valuable contribution to ensure reliability and prevent regressions.
    *   Tests could cover:
        *   File path resolution (`get_paths`).
        *   `TagDoc` initialization and HTML/text extraction.
        *   `TagExtractor` logic with mock NLP results.
        *   CLI argument parsing and overall tool execution.
*   **Submitting Changes:**
    1.  Fork the repository on GitHub.
    2.  Create a new branch for your feature or bug fix.
    3.  Make your changes, ensuring to update or add documentation as needed.
    4.  If adding new features or fixing bugs, consider adding tests.
    5.  Push your changes to your fork.
    6.  Submit a Pull Request (PR) to the main repository.
*   **Versioning:** The version is specified in `setup.py`. If making significant changes, consider discussing a version bump.

### License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

*This README was significantly expanded by an AI assistant based on the existing codebase and README.*
