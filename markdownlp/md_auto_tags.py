#!/usr/bin/env python3

import logging
import math
from pathlib import Path

import markdown
from slugify import slugify

try:
    import spacy
    from pattern.text.en import singularize, wordnet

    spacy.load("en_core_web_sm")
except Exception:
    import nltk

    nltk.download("omw-1.4")
    import spacy

    spacy.cli.download("en_core_web_sm")
    import sys

    logging.error("Packages installed. Please run the tool again.")
    sys.exit(1)

import fire
from bs4 import BeautifulSoup
from pke.lang import stopwords
from pke.supervised import Kea
from pke.unsupervised import KPMiner, TfIdf, TopicalPageRank

from html22text import html22text
from yaplon import oyaml

MODELS_PARAMS = {
    TfIdf: (3, 1),
    TopicalPageRank: (3, 300),
    Kea: (2, 400),
    KPMiner: (3, 1),
}

MODELS = {
    model.__name__: {"model": model(), "best_factor": params[0], "weight": params[1]}
    for model, params in MODELS_PARAMS.items()
}


class TagDoc:
    def __init__(self, md_path, html_path="", selector="html", tags_global_no=None):
        self.md_path = Path(md_path).resolve()
        self.md = self.md_path.read_text(encoding="utf-8")
        self.html_path = Path(html_path).resolve()
        if not html_path.is_file() or self.html_path == self.md_path:
            self.html_path = self.md_path
            self.html = self.html_from_markdown()
        else:
            self.html = self.html_path.read_text(encoding="utf-8")
        self.selector = selector
        self.tags_global_no = tags_global_no or []
        self.load()

    def load(self):
        self.soup = BeautifulSoup(self.html, "html.parser")
        self.text = html22text(
            self.html,
            markdown=False,
            selector=self.selector,
            base_url="",
            plain_tables=True,
            open_quote="“",
            close_quote="”",
            block_quote=True,
            default_image_alt="",
            kill_strikethrough=False,
            kill_tags=[],
            file_ext="",
        )
        self.init_md_meta_doc()
        self.init_tags_from_md()

    def html_from_markdown(self):
        html = markdown.markdown(
            self.md,
            extensions=[
                "abbr",
                "admonition",
                "attr_list",
                "def_list",
                "full_yaml_metadata",
                "md_in_html",
                "toc",
                "tables",
                "pymdownx.betterem",
                "pymdownx.caret",
                "pymdownx.keys",
                "pymdownx.details",
                "pymdownx.mark",
                "pymdownx.saneheaders",
            ],
        )
        return (
            f"""<html><head><meta charset="UTF-8"></head><body>{html}</body></html>"""
        )

    def init_md_meta_doc(self):
        md_lines = self.md.split("\n")
        meta = []
        linej = 0
        if len(md_lines) and md_lines[0] == "---":
            for linei, line in enumerate(md_lines[1:]):
                if line == "---":
                    linej = linei + 2
                    break
                else:
                    meta.append(line)
        self.md_body = "\n".join(md_lines[linej:])
        meta_text = "\n".join(meta)
        self.md_meta = oyaml.read_yaml(meta_text)
        if not self.md_meta:
            self.md_meta = {}

    def init_tags_from_md(self):
        self.tags = self.md_meta.get("tags", [])
        self.tags_no = self.tags_global_no + self.md_meta.get("tags-no", [])
        self.tags_yes = self.md_meta.get("tags-yes", [])

    def build_md(self):
        self.md = "---\n"
        self.md += oyaml.yaml_dumps(self.md_meta)
        self.md += "---\n"
        self.md += self.md_body

    def save(self):
        self.build_md()
        self.md_path.write_text(self.md, encoding="utf-8")

    def get_tags_text(self, tags):
        return ". ".join(
            [
                ". ".join([h.get_text() for h in self.soup.find_all(tag)])
                for tag in tags.split(" ")
            ]
        )


class TagExtractor:
    def __init__(
        self,
        lang: str = "en",
        slug: bool = True,
        prefix: str = "#",
        retag: bool = False,
        auto_only: bool = False,
        boost_headings: bool = False,
        stop_words: list = [],
    ):
        self.lang = lang
        self.tag_slug = slug
        self.tag_sep = "-" if slug else " "
        self.tag_prefix = prefix
        self.retag = retag
        self.auto_only = auto_only
        if boost_headings:
            self.tag_boost = {"h1": 64, "h2 h3": 16, "h4 h5 h6": 4}
        else:
            self.tag_boost = {}
        self.stop_words = self.get_stop_words(stop_words)
        logging.debug(f"""{self.stop_words=}""")

    def get_stop_words(self, stop_words):
        return stopwords.get(self.lang, set()) | set(stop_words)

    def load(self, doc: TagDoc):
        self.doc = doc
        self.tagd = dict.fromkeys(self.doc.tags_yes, 65535)
        self.length = len(self.doc.text.split())
        self.do = True
        if self.doc.md_meta.get("tags-done", False):
            self.do = False
        if self.retag:
            self.do = True
        if self.auto_only and not self.doc.md_meta.get("tags-auto", False):
            self.do = False
        if not self.length or self.doc.md_meta.get("tags-none", False):
            self.do = False

    def prep_tag(self, tag):
        if self.lang in ("en"):
            new_words = []
            for word in tag.split():
                sing = singularize(word)
                word = sing if wordnet.synsets(sing, pos=wordnet.NOUN) else word
                new_words.append(word)
            tag = " ".join(new_words)

        if self.tag_slug:
            tag = slugify(
                tag,
                entities=True,
                decimal=True,
                hexadecimal=True,
                lowercase=True,
            )
        return f"{self.tag_prefix}{tag}"

    def get_freqtags_from_text_with_extractor(self, text, extractor, n_best):
        extractor.load_document(
            text, language=self.lang, stoplist=self.stop_words, normalization=None
        )
        extractor.candidate_selection()  # pos={'NOUN', 'PROPN', 'ADJ'})
        extractor.candidate_weighting()
        return extractor.get_n_best(n=n_best)

    def freqtags_from_text_with_model(self, model, text, boost=1):
        try:
            tagt_model = self.get_freqtags_from_text_with_extractor(
                text, model["model"], self.max_tags * model["best_factor"]
            )
            logging.debug(
                f"""\n##### MODEL {model["model"].__class__}:\n     {tagt_model}"""
            )
        except Exception:
            tagt_model = []
        for tag, tag_freq in tagt_model:
            tag = self.prep_tag(tag)
            if tag not in self.doc.tags_no:
                tag_freq = (
                    tag_freq * model["weight"] * boost / len(tag.split(self.tag_sep))
                )
                if tag in self.tagd:
                    self.tagd[tag] += tag_freq
                else:
                    self.tagd[tag] = tag_freq

    def extract(self):
        if self.do:
            logging.info(
                f"""\n## Adding tags:\n- from HTML: "{str(self.doc.html_path)}"\n- to MD: "{str(self.doc.md_path)}" """
            )
            self.max_tags = int((math.log(self.length, 1.25) - 9) / 3) * 2

            for model_name, model in MODELS.items():
                logging.debug(f"""\n### Extracting tags with MODEL: {model_name}""")
                for boost_htags, boost in self.tag_boost.items():
                    logging.debug(f"""\n#### HTAGS: {boost_htags}""")
                    self.freqtags_from_text_with_model(
                        model, self.doc.get_tags_text(boost_htags), boost
                    )
                logging.debug("""\n#### ALL TEXT""")
                self.freqtags_from_text_with_model(model, self.doc.text, 1)
            self.tagd = dict(
                sorted(
                    self.tagd.items(), key=lambda tag_freq: tag_freq[1], reverse=True
                )
            )

    def store(self):
        if self.do:
            self.doc.tags = list(self.tagd.keys())[: self.max_tags]
            self.doc.md_meta["tags"] = self.doc.tags
            self.doc.md_meta["tags-done"] = True
            logging.info(
                f"""\n## New tags in:\n"{str(self.doc.md_path)}":\n{self.tagd}"""
            )


def get_paths(md_path, html_path=""):
    if not html_path:
        html_path = md_path
    md_path = Path(md_path).resolve()
    html_path = Path(html_path).resolve()
    if Path(md_path).is_dir():
        md_paths = list(Path(md_path).glob("**/*.md"))
        paths = {}
        for md_p in md_paths:
            md_pstem = Path(md_p.parent, md_p.stem)
            html_pstem = Path(str(md_pstem).replace(str(md_path), str(html_path)))
            html_p = Path(f"""{str(html_pstem)}.html""")
            if not html_p.is_file():
                html_p = Path(html_pstem, "index.html")
            if not html_p.is_file():
                html_p = md_p
            if html_p.is_file():
                logging.debug(
                    f"""\n## Analyzing:\n- from HTML: "{str(html_p)}"\n- to MD: "{str(md_p)}" """
                )
                paths[md_p] = html_p
            else:
                logging.warning(f"""\## HTML file does not exist:\n"{html_p}" """)
    else:
        paths = {md_path: html_path}
    return paths


def md_auto_tags(
    md_path: Path | str,
    html_path: Path | str = "",
    selector: str = "html",
    boost_headings: bool = False,
    lang: str = "en",
    slug: bool = False,
    prefix: str = "",
    auto_only: bool = False,
    retag: bool = False,
    tags_global_no: str = "",
    stop_words: str = "",
    verbose: bool = False,
):
    """md_auto_tags

    This CLI tool needs a Markdown file (or recursive folder) and optionally a corresponding file or folder with .html files. It reads the HTML files (or converts the Markdown to HTML on the fly with some default extensions), uses some NLP techniques to extract keywords (important phrases) from the HTML and writes them into the Markdown metadata `tags` list.

    The tool is a good companion for the MkDocs Material `tags` plugin:
    https://squidfunk.github.io/mkdocs-material/setup/setting-up-tags/

    The tool is quite slow, so by default it only processes files that have not been previously processed by it.

    The tool uses the following Markdown YAML metadata entries:

    - `tags:`: The tool will put the generated tags into this list.
    - `tags-yes`: List of tags the tool will add to the generated tags.
    - `tags-no`: List of tags the tool will not put into `tags` in addition to the global list specified with `--tags_global_no`.
    - `tags-done: true`: Unless `--retag` is specified, the tool will not generate tags if this is present. Remove this if you change your Markdown file content and you want it retagged.
    - `tags-auto: true`: If `--auto_only` is specified, the tool will generate tags only if this is present. The tool writes this entry after it has processed a file.
    - `tags-none: true`: The tool will not generate any tags if this is present.

    Command-line args:
        md_path (Union[Path, str]): path to Markdown file or folder
        html_path (Union[Path, str], optional): path to corresponding HTML file or folder
        selector (str, optional): CSS selector to restrict text extraction. Defaults to "html", for MkDocs Material sites use "article".
        boost_headings (bool, optional): Considers H1-H6 tag text more important in keyword extraction. Defaults to False.
        lang (str, optional): Language of text. Defaults to "en". For non-English texts, you need to install some NLP models yourself.
        slug (bool, optional): If True, the extracted tags are slugified (converted to lowercase and spaces replaced with hyphens). Defaults to False.
        prefix (str, optional): Prefix for each tag. If tags are slugified, you could use "#". Defaults to "".
        auto_only (bool, optional): If True, the tool will generate tags only if `tags-auto: true` is present in the Markdown metadata. Defaults to False.
        retag (bool, optional): If False, the tool will not process Markdown files that have `tags-done: true` in the Markdown metadata. If True, it will process these files as well. Defaults to False.
        tags_global_no (str, optional): Space-separated list of tags which the tool will not put into `tags`, on top of the file-specific exclusions in the `tags-no` Markdown metadata list. Defaults to "".
        stop_words (str, optional): Space-separated list of additional stop words for NLP analysis. Defaults to "".
        verbose (bool, optional): Print additional info during processing. Defaults to False.
    """
    logginglevel = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=logginglevel)
    logging.info(f"""\n# AUTO-TAGGING:\n- from: "{html_path}"\n- to: "{md_path}" """)
    paths = get_paths(Path(md_path).resolve(), Path(html_path).resolve())
    tags_global_no = tags_global_no.split(" ") if tags_global_no else []
    logging.debug(f"""{tags_global_no=}""")
    tagger = TagExtractor(
        lang=lang,
        slug=slug,
        prefix=prefix,
        retag=retag,
        auto_only=auto_only,
        boost_headings=boost_headings,
        stop_words=stop_words.split(" ") if stop_words else [],
    )
    for md_path, html_path in paths.items():
        tagger.load(
            TagDoc(md_path, html_path, selector=selector, tags_global_no=tags_global_no)
        )
        # if "topics-auto" in tagger.doc.md_meta:  # REMOVE LATER
        #    del tagger.doc.md_meta["topics-auto"]
        tagger.extract()
        tagger.store()
        tagger.doc.save()


def cli():
    fire.core.Display = lambda lines, out: print(*lines, file=out)
    fire.Fire(md_auto_tags)


if __name__ == "__main__":
    cli()
