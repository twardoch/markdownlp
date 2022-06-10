//var unified = require("unified");

const G = require("os").homedir() + "/.npm-packages/lib/node_modules/";

function grequire(mod) {
    return require(G + mod);
}

var unified = grequire('unified');

var remarkConfig = {
    settings: {
        bullet: "-",
        closeAtx: false,
        commonmark: false,
        emphasis: "_",
        entities: false,
        fence: "`",
        fences: true,
        footnotes: true,
        gfm: false,
        incrementListMarker: true,
        listItemIndent: "1",
        looseTable: false,
        paddedTable: true,
        pedantic: false,
        rule: "-",
        ruleRepetition: 3,
        ruleSpaces: false,
        setext: false,
        spacedTable: true,
        strong: "*",
        yaml: true,
    },
    plugins: {
        frontmatter: null,
        github: {
            repository: "Fontlab/fl",
            mentionStrong: false,
        },
        "validate-links": {
            repository: "Fontlab/FontLabVI-help.wiki",
        },
        "heading-gap": {
            1: {
                after: "\n",
                before: "\n\n",
            },
            2: {
                after: "\n",
                before: "\n",
            },
        },
        "inline-links": null,
        slug: null,
        "squeeze-paragraphs": null,
        "yaml-config": null,
        //"heading-trailing-spaces": null,
        //"kbd-plus": null,
        //mark: null,
        "embed-images": null,
        "external-links": {
            target: "_blank",
        },
        gemoji: null,
        "parse-yaml": null,
        toc: null,
        /*"wiki-link-a": {
                                                                                                        stringify: false,
                                                                                                        mdPrefix: "",
                                                                                                        mdSuffix: ".md",
                                                                                                        mdSpace: "-",
                                                                                                        htmlClass: "wikilink",
                                                                                                        htmlPrefix: "../",
                                                                                                        htmlSuffix: "/",
                                                                                                        htmlSpace: "-",
                                                                                                    },*/
        lint: null,
        "lint-alphabetize-lists": false,
        "lint-blockquote-indentation": "consistent",
        "lint-books-links": true,
        "lint-checkbox-character-style": {
            checked: "x",
            unchecked: " ",
        },
        "lint-checkbox-content-indent": true,
        "lint-code-block-style": "fenced",
        "lint-definition-case": true,
        "lint-definition-spacing": true,
        "lint-emphasis-marker": "_",
        "lint-fenced-code-flag": {
            allowEmpty: true,
        },
        "lint-fenced-code-marker": "`",
        "lint-file-extension": "md",
        "lint-final-definition": true,
        "lint-final-newline": true,
        "lint-first-heading-level": 1,
        "lint-hard-break-spaces": true,
        "lint-heading-increment": true,
        "lint-heading-style": "atx",
        "lint-link-title-style": "consistent",
        "lint-list-item-bullet-indent": false,
        "lint-list-item-content-indent": true,
        "lint-list-item-indent": "tab-size",
        "lint-list-item-spacing": {
            checkBlanks: true,
        },
        "lint-maximum-heading-length": 200,
        "lint-maximum-line-length": 1000,
        "lint-no-auto-link-without-protocol": false,
        "lint-no-blockquote-without-marker": false,
        "lint-no-consecutive-blank-lines": true,
        "lint-no-dead-urls": false,
        "lint-no-duplicate-definitions": true,
        "lint-no-duplicate-headings": true,
        "lint-no-emphasis-as-heading": true,
        "lint-no-empty-sections": true,
        "lint-no-file-name-articles": true,
        "lint-no-file-name-consecutive-dashes": true,
        "lint-no-file-name-irregular-characters": "\\\\.a-zA-Z0-9_\\$\\-",
        "lint-no-file-name-mixed-case": true,
        "lint-no-file-name-outer-dashes": true,
        "lint-no-heading-content-indent": true,
        "lint-no-heading-indent": true,
        "lint-no-heading-punctuation": false,
        "lint-no-html": false,
        "lint-no-inline-padding": true,
        "lint-no-literal-urls": false,
        "lint-no-missing-blank-lines": true,
        "lint-no-multiple-toplevel-headings": true,
        "lint-no-shell-dollars": true,
        "lint-no-shortcut-reference-image": false,
        "lint-no-shortcut-reference-link": false,
        "lint-no-table-indentation": true,
        "lint-no-tabs": true,
        "lint-no-undefined-references": false,
        "lint-no-unused-definitions": true,
        "lint-ordered-list-marker-style": ".",
        "lint-ordered-list-marker-value": "ordered",
        "lint-rule-style": "---",
        "lint-strong-marker": "*",
        "lint-table-cell-padding": "padded",
        "lint-table-pipe-alignment": true,
        "lint-table-pipes": true,
        "lint-unordered-list-marker-style": "-",

        retext: unified()
            .use(grequire("retext-stringify"))
            .use(grequire("retext-english"))
            .use(grequire("retext-spell"), {
                dictionary: grequire("dictionary-en"),
                //personal: dictionary,
            })
            .use(grequire("retext-latin"))
            //.use(grequire("retext-18f-simplify"))
            //.use(grequire("retext-assuming"))
            .use(grequire("retext-contractions"))
            .use(grequire("retext-diacritics"))
            .use(grequire("retext-emoji"))
            .use(grequire("retext-equality"))
            //.use(grequire("retext-google-styleguide"))
            //.use(grequire("retext-ibmstyleguide"))
            .use(grequire("retext-indefinite-article"))
            .use(grequire("retext-intensify"))
            .use(grequire("retext-keywords"))
            //.use(grequire("retext-overuse"))
            .use(grequire("retext-passive"))
            .use(grequire("retext-profanities"))
            .use(grequire("retext-quotes"))
            .use(grequire("retext-readability"), { age: 14 })
            .use(grequire("retext-redundant-acronyms"))
            .use(grequire("retext-repeated-words"))
            .use(grequire("retext-simplify"))
            .use(grequire("retext-syntax-mentions-channels"))
            .use(grequire("retext-syntax-mentions"))
            .use(grequire("retext-syntax-urls"))
            .use(grequire("retext-usage"))
            .use(grequire("retext-textlint"), {
                plugins: [
                    "textlint-rule-no-todo",
                    "textlint-rule-spellchecker",
                    "textlint-rule-diacritics",
                    "textlint-rule-apostrophe",
                ],
                rules: {
                    diacritics: {},
                    "no-todo": true,
                    apostrophe: true,
                    "terminology": {
                        "defaultTerms": true
                    }
                },
            }),
        //.use(grequire("retext-wordusage")),

        textr: {
            options: {
                locale: "en-us",
            },
            plugins: [
                "typographic-apostrophes",
                "typographic-apostrophes-for-possessive-plurals",
                "typographic-arrows",
                "typographic-colon",
                "typographic-copyright",
                "typographic-ellipses",
                "typographic-en-dashes",
                "typographic-exclamation-mark",
                "typographic-guillemets",
                //"typographic-markdown",
                "typographic-math-symbols",
                "typographic-numbers",
                "typographic-percent",
                "typographic-permille",
                "typographic-question-mark",
                "typographic-quotes",
                "typographic-registered-trademark",
                "typographic-semicolon",
                "typographic-single-spaces",
                "typographic-trademark",
            ],
        },
        "lint-write-good": [
            "warn",
            {
                passive: true,
                illusion: true,
                so: true,
                thereIs: true,
                weasel: true,
                adverb: true,
                tooWordy: true,
                cliches: true,
                eprime: false,
            },
        ],
    },
};

module.exports = remarkConfig;