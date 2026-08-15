import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "lde"))

from md_render import normalize_page_anchors, render_md_to_body


class RenderFoldableSectionsTest(unittest.TestCase):
    def test_heading_and_block_markers_become_foldable(self) -> None:
        md = "# Intro\n\nSome text\n\n## Details\n\nMore text\n\n::: expand Título\n\nInside\n:::"

        html = render_md_to_body(md)

        self.assertIn('<details class="foldable-section foldable-heading"', html)
        self.assertIn('<summary class="foldable-summary">Intro</summary>', html)
        self.assertIn('<details class="foldable-section foldable-block', html)
        self.assertIn("Título", html)
        # Preview default: sections open so page chrome is visible
        self.assertIn("<details ", html)
        self.assertIn(" open", html)

    def test_prose_inside_foldables_becomes_paragraphs(self) -> None:
        """Regression: long-form books (ESE) need real <p> tags, not raw text."""
        md = (
            "# Chapter\n\n"
            "First paragraph with enough words.\n\n"
            "Second paragraph continues the thought.\n\n"
            "::: center\n\n"
            "Centered line one.\n\n"
            "Centered line two.\n"
            ":::\n"
        )
        html = render_md_to_body(md)
        self.assertGreaterEqual(html.count("<p>"), 4)
        self.assertIn("<p>First paragraph with enough words.</p>", html)
        self.assertIn("<p>Second paragraph continues the thought.</p>", html)
        self.assertIn("<p>Centered line one.</p>", html)

    def test_page_anchors_become_page_chrome(self) -> None:
        md = (
            "# Book\n\n"
            "[]{#page-1}\n\n"
            "Opening line of page one.\n\n"
            "[]{#page-2}\n\n"
            "Start of page two.\n"
        )
        html = render_md_to_body(md)
        self.assertIn('id="page-1"', html)
        self.assertIn('id="page-2"', html)
        self.assertIn('data-page="1"', html)
        self.assertIn('class="pdf-page-start"', html)
        self.assertIn('class="pdf-page-footer"', html)
        self.assertIn("Opening line of page one.", html)
        self.assertIn("Start of page two.", html)
        # page chrome must not live inside the heading label
        self.assertNotRegex(
            html,
            r'<summary[^>]*>[^<]*<div class="pdf-page-start"',
        )
        self.assertNotIn("PDFPAGE", html)
        self.assertNotIn("[]{#page-", html)

    def test_inline_page_anchor_does_not_orphan_p(self) -> None:
        md = "# Q\n\nLeading sentence []{#page-80} continues after the marker.\n"
        html = render_md_to_body(md)
        self.assertIn('id="page-80"', html)
        self.assertEqual(html.count("<p"), html.count("</p>"))
        self.assertIn("continues after the marker", html)
        self.assertIn("Leading sentence", html)
        # chrome is block-level between paragraphs, not inside one
        self.assertNotRegex(
            html,
            r"<p[^>]*>[^<]*<div class=\"pdf-page-start\"",
        )

    def test_mid_toc_page_anchor_keeps_nested_lists(self) -> None:
        """Page markers between nested TOC lines must not become <pre> code."""
        md = (
            "# Book\n\n"
            "::: expand Sumário\n"
            "Intro line with `Ctrl + F`.\n\n"
            "- [Root](#root)\n"
            "  - [Child A](#a)\n"
            "    - [Grand](#g)\n"
            " []{#page-6} \n"
            "    - [Child B](#b)\n"
            "      - [Grand B](#gb)\n"
            " []{#page-7} \n"
            "    - [Child C](#c)\n"
            ":::\n"
        )
        html = render_md_to_body(md)
        self.assertNotIn("codehilite", html)
        self.assertNotIn("<pre", html)
        self.assertIn('id="page-6"', html)
        self.assertIn('id="page-7"', html)
        self.assertIn('href="#b"', html)
        self.assertIn("Child B", html)
        self.assertIn("Child C", html)
        # nested lists survived
        self.assertGreaterEqual(html.count("<ul>"), 2)

    def test_normalize_attaches_anchor_only_line_to_previous(self) -> None:
        md = "- item A\n []{#page-3} \n- item B\n"
        norm = normalize_page_anchors(md)
        self.assertIn("<!--PDFPAGE:3-->", norm)
        self.assertIn("item A", norm)
        # no free-standing anchor-only line left
        self.assertIsNone(re.search(r"^\s*<!--PDFPAGE:3-->\s*$", norm, re.M))
        self.assertIn("item A", norm.split("<!--PDFPAGE:3-->")[0])


if __name__ == "__main__":
    unittest.main()
