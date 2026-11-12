import collections
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from pendencias_integralidade import REGISTRO, carregar
from plano import Item
import progresso


class ProgressoTest(unittest.TestCase):
    def test_excesso_de_uma_serie_nao_preenche_lacuna_de_outra(self):
        a = Item('setor', 'a', 'federal/a', 2, 1, 'fonte')
        b = Item('setor', 'b', 'federal/b', 2, 1, 'fonte')
        desconhecida = Item('setor', 'c', 'federal/c', None, 1, 'fonte')
        self.assertEqual(progresso.totais([(a, 10), (b, 0), (desconhecida, 3)]), (13, 2, 4, 3))

    def test_pendente_preservado_fora_da_contagem_e_download_fora_do_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            subprocess.run(['git', 'init', '-q', tmp], check=True)
            pasta = raiz / 'federal/decretos'
            pasta.mkdir(parents=True)
            for nome in ('apto.md', 'pendente.md'):
                (pasta / nome).write_text('# Ato\n')
            registro = raiz / REGISTRO
            registro.parent.mkdir(parents=True)
            registro.write_text(json.dumps({'pendentes': [{'path': 'federal/decretos/pendente.md',
                'sha256_md': 'a' * 64, 'motivo': 'anexo pendente', 'evidencia': 'fonte oficial'}]}))
            subprocess.run(['git', 'add', '.'], cwd=raiz, check=True)
            (pasta / 'nao-publicado.md').write_text('# Outro\n')
            pendentes = carregar(raiz, True)
            item = Item('setor', 'decretos', 'federal/decretos', 10, 1, 'fonte')
            with patch.object(progresso, 'RAIZ', tmp), patch.object(progresso, 'PLANO', [item]):
                index, _ = progresso.medir_git(pendentes)
                worktree, _ = progresso.medir(pendentes)
            self.assertEqual(index[0][1], 1)
            self.assertEqual(worktree[0][1], 2)
            self.assertTrue((pasta / 'pendente.md').exists())

    def test_ler_progresso_le_o_markdown_gerado(self):
        a = Item('setor', 'a', 'federal/a', 2, 1, 'fonte')
        sem = Item('setor', 's', 'federal/s', None, 1, 'fonte')
        b = Item('setor', 'b', 'federal/b', 10, 2, 'fonte')
        c = Item('setor', 'c', 'federal/c', 10, 3, 'fonte')
        medidas = [(a, 1), (sem, 3), (b, 5), (c, 3)]
        with patch.object(progresso, 'por_setor', lambda: {'setor': [a, sem, b, c]}):
            texto = progresso.markdown(medidas, collections.Counter())
        lido = progresso.ler_progresso(texto)
        self.assertEqual(lido['total'], 12)
        self.assertEqual(lido['fases'][1]['documentos'], 4)
        self.assertEqual(lido['fases'][2]['documentos'], 5)
        self.assertEqual(lido['fases'][3]['documentos'], 3)
        self.assertEqual(lido['fases'][1]['cobertura'], 50.0)
        self.assertEqual(lido['fases'][2]['cobertura'], 50.0)
        self.assertEqual(lido['fases'][3]['cobertura'], 30.0)

    def test_ler_readme_acervo_le_a_tabela_o_acervo(self):
        texto = (
            "## O acervo\n\n"
            "Em 08/11/2026 eram **12.345 documentos**.\n\n"
            "| Fase | Escopo | Documentos | Cobertura da meta |\n"
            "| --- | --- | ---: | ---: |\n"
            "| 1 | Legislação federal e leis estaduais | 1.000 | 10,5% |\n"
            "| 2 | Infralegal e jurisprudência | 2.000 | 20,0% |\n"
            "| 3 | Direito municipal | 9.345 | 1,5% |\n"
            "| | **Total** | **12.345** | |\n"
            "\n---\n"
        )
        lido = progresso.ler_readme_acervo(texto)
        self.assertEqual(lido['data'], '08/11/2026')
        self.assertEqual(lido['total'], 12345)
        self.assertEqual(lido['fases'][1], {'documentos': 1000, 'cobertura': 10.5})
        self.assertEqual(lido['fases'][2], {'documentos': 2000, 'cobertura': 20.0})
        self.assertEqual(lido['fases'][3], {'documentos': 9345, 'cobertura': 1.5})

    def test_desenhar_destaca_subtotal_fases_1_e_2(self):
        a = Item('setor1', 'a', 'federal/a', 100, 1, 'fonte')
        b = Item('setor2', 'b', 'federal/b', 100, 2, 'fonte')
        c = Item('setor3', 'c', 'municipais/c', 1800, 3, 'fonte')
        medidas = [(a, 80), (b, 40), (c, 0)]
        with patch.object(progresso, 'por_setor', lambda: {'setor1': [a], 'setor2': [b], 'setor3': [c]}):
            svg = progresso.desenhar(medidas)
        ET.fromstring(svg)
        self.assertIn('Fases 1 e 2 (federal e estadual, exceto estimativa municipal) · 120 / ~200', svg)
        self.assertIn('>60.0%<', svg)
        self.assertIn('>6.0%<', svg)

    def test_readme_acervo_coincide_com_progresso(self):
        raiz = Path(progresso.RAIZ)
        readme_path, prog_path = raiz / 'README.md', raiz / 'PROGRESSO.md'
        if not readme_path.is_file() or not prog_path.is_file():
            self.skipTest('README.md e PROGRESSO.md fora do checkout esparso do CI')
        readme = progresso.ler_readme_acervo(readme_path.read_text(encoding='utf-8'))
        prog = progresso.ler_progresso(prog_path.read_text(encoding='utf-8'))
        self.assertEqual(readme['data'], prog['data'])
        self.assertEqual(readme['total'], prog['total'])
        self.assertEqual(readme['fases'], prog['fases'])


if __name__ == '__main__':
    unittest.main()
