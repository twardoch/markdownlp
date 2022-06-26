# markdownlp

Collection of NLP tools for Markdown (mostly using Python).

## Installation

```
python3 -m pip install git+https://github.com/twardoch/markdownlp
```

## Usage

### `md_auto_tags`

The `md_auto_tags` tool is a CLI tool needs a Markdown file (or recursive folder) and optionally a corresponding file or folder with .html files. It reads the HTML files (or converts the Markdown to HTML on the fly with some default extensions), uses some NLP techniques to extract keywords (important phrases) from the HTML, and writes them into the Markdown metadata `tags` list.

The tool is quite slow, so by default it only processes files that have not been previously processed by it. The tool is a good companion for the MkDocs Material [`tags`](https://squidfunk.github.io/mkdocs-material/setup/setting-up-tags/) plugin.

The tool can work in just a Markdown file. Then it will generate the HTML version on the fly, extract its text and then the tags from it.

But it works better if you give it a path to a Markdown file and a path to a corresponding HTML file, or even a source folder with Markdown files and a reference folder which has corresponding HTML files in the same structure. This is useful if you run MkDocs with various plugins, so that the final HTML files include some additional texts. You can tell the tool to only analyze the content of a particular selector, for example `article` rather than the entire HTML file.

#### Command-line usage

```
md_auto_tags MD_PATH --html_path=HTML_PATH \
  --selector=html --boost_headings --lang=en \
  --slug --prefix="" --auto_only --retag \
  --tags_global_no="" --stop_words="" --verbose
```

You can also invoke it via `python3 -m markdownlp.md_auto_tags MD_PATH ...`

- `MD_PATH`: path to Markdown file or folder
- `--html_path=PATH`: optional path to corresponding HTML file or folder
- `--selector="html"`: CSS selector to restrict text extraction. Defaults to "html", for MkDocs Material sites use "article".
- `--boost_headings`: If set, sonsiders H1-H6 tag text more important in keyword extraction.
- `--lang="en"`: Language of text. Defaults to "en". For non-English texts, you need to install some NLP models yourself (and possibly modify the code, I haven’t tested the tool with non-English text).
- `--slug`: If set, the extracted tags are slugified (converted to lowercase and spaces replaced with hyphens).
- `--prefix=""`: Prefix for each tag. If tags are slugified, you could use "#". Defaults to "".
- `--auto_only`: If set, the tool will generate tags only if `tags-auto: true` is present in the Markdown metadata.
- `--retag`: If not set, the tool will not process Markdown files that have `tags-done: true` in the Markdown metadata. If set, it will process these files as well.
- `--tags_global_no=""`: Space-separated list of tags which the tool will not put into `tags`, on top of the file-specific exclusions in the `tags-no` Markdown metadata list. Defaults to "".
- `--stop_words=""`: Space-separated list of additional stop words for NLP analysis. Defaults to "".
- `--verbose`: If set, prints additional info during processing.

#### Usage of Markdown YAML metadata

The tool uses the following Markdown YAML metadata entries:

- `tags:`: The tool will put the generated tags into this list.
- `tags-yes`: List of tags the tool will add to the generated tags.
- `tags-no`: List of tags the tool will not put into `tags` in addition to the global list specified with `--tags_global_no`.
- `tags-done: true`: Unless `--retag` is specified, the tool will not generate tags if this is present. Remove this if you change your Markdown file content and you want it retagged.
- `tags-auto: true`: If `--auto_only` is specified, the tool will generate tags only if this is present. The tool writes this entry after it has processed a file.
- `tags-none: true`: The tool will not generate any tags if this is present.

