from __future__ import annotations

import unittest

from _local_package import load_local_package

load_local_package()
from omj.routing.catalog_questions import is_file_or_text_lookup_question, is_skill_catalog_question


class CatalogQuestionTests(unittest.TestCase):
    def test_workflow_catalog_questions_are_detected(self) -> None:
        cases = (
            "what can OMJ do?",
            "what can I do with OMJ?",
            "what does OMJ do?",
            "how can OMJ help my team?",
            "Can OMJ help with planning, research, and coding?",
            "what can OMJ do for planning/research/coding?",
            "Can OMJ help with planning/research/coding?",
            "OMJ로 뭐 할 수 있어?",
            "OMJ가 뭐 해줄 수 있어?",
            "OMJ는 뭘 도와줘?",
            "OMJ가 우리 팀에서 어떻게 쓰여?",
            "OMJ로 계획/리서치/코딩까지 도와줄 수 있어?",
            "OMJ에서 deep-interview/ralplan/loop는 뭐야?",
            "OMJ로 할 수 있는 workflow가 뭐야?",
            "OMJ 명령어 뭐 있어?",
            "skill들은 뭐 있어?",
            "what OMJ workflows are available?",
            "¿Qué comandos de OMJ están disponibles?",
            "Quelles commandes OMJ sont disponibles ?",
            "Welche OMJ Workflows gibt es?",
            "OMJで使えるスキルは？",
            "OMJ 有哪些工作流？",
            "Quais workflows do OMJ estão disponíveis?",
            "Какие команды OMJ доступны?",
        )

        for message in cases:
            with self.subTest(message=message):
                self.assertTrue(is_skill_catalog_question(message))

    def test_new_and_legacy_brand_capability_questions_are_detected(self) -> None:
        # Rule B: the renamed product brand (oh-my-jeo / oh my jeo) must be accepted
        # for the picker fast-path, while the legacy brand (oh-my-hermes) stays
        # backward-compatible.
        new_brand = (
            "what can oh-my-jeo do?",
            "what can I do with oh-my-jeo?",
            "what does oh-my-jeo do?",
            "how can oh-my-jeo help my team?",
            "what is oh-my-jeo useful for?",
            "oh-my-jeo로 뭐 할 수 있어?",
            "oh-my-jeo로 할 수 있는 workflow가 뭐야?",
            "oh-my-jeo 기능 뭐 있어?",
            "what can oh my jeo do?",
        )
        legacy_brand = (
            "what can oh-my-hermes do?",
            "what does oh-my-hermes do?",
            "oh-my-hermes로 뭐 할 수 있어?",
            "what can oh my hermes do?",
        )
        for message in new_brand + legacy_brand:
            with self.subTest(message=message):
                self.assertTrue(is_skill_catalog_question(message))

    def test_operator_command_questions_are_not_catalog_questions(self) -> None:
        cases = (
            "show me the command to install OMJ",
            "what command is available to install OMJ?",
            "what commands are available to install OMJ?",
            "what command should I run to verify installation?",
            "what can OMJ do to install itself?",
            "¿Qué comando debería ejecutar para instalar OMJ?",
            "quelle commande dois-je exécuter pour installer OMJ?",
            "OMJ 설치 명령어 알려줘",
            "doctor 확인 명령어 뭐야?",
        )

        for message in cases:
            with self.subTest(message=message):
                self.assertFalse(is_skill_catalog_question(message))

    def test_generic_debugging_and_file_questions_do_not_open_catalog(self) -> None:
        cases = (
            "what skills are needed to debug this Python error?",
            "which workflow should I use for this bug?",
            "what does OMJ do in src/omj/routing/catalog_questions.py?",
            "explain what OMJ does in this README section",
            "search docs/WORKFLOWS.md for loop",
            "show img-summary in README.md",
            "how can Hermes help my team?",
            "list commands in this file",
            "show workflows mentioned in docs/WORKFLOWS.md",
            "which files mention skill routing?",
            "list files that mention command injection",
            "이 파일에서 command injection 언급 목록 찾아줘",
            "이 파일에서 기능 목록 찾아줘",
            "이 경로에서 workflow 언급 찾아줘",
            "프리렌이 OMJ 안 쓰고 일반 도구로 이미지 만들었어",
            "이미지 생성 요청을 했는데 OMJ를 안 썼어",
        )

        for message in cases:
            with self.subTest(message=message):
                self.assertFalse(is_skill_catalog_question(message))

    def test_release_claim_review_is_not_file_lookup_fallback(self) -> None:
        message = "릴리즈 전에 README 주장과 실제 기능이 맞는지 검토해줘"

        self.assertFalse(is_skill_catalog_question(message))
        self.assertFalse(is_file_or_text_lookup_question(message))


if __name__ == "__main__":
    unittest.main()
