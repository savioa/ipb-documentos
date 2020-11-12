"""Representa a constituição da IPB.

Classes:
    Constituicao
    Capitulo
    Secao
    Artigo
    Paragrafo
    Caput
    Alinea
    Utilitario
"""

import re
import sys
from collections import namedtuple
from operator import attrgetter
import roman
from yattag import Doc

CLASSES_TITULO = 'title is-1 has-text-centered'
CLASSES_SUBTITULO = 'title is-3 has-text-centered'
CLASSES_SECAO = 'title is-5 has-text-centered'

ESCAPE_ALERTA = '\033[33m'
ESCAPE_ERRO = '\033[31m'
ESCAPE_ENDC = '\033[0m'


class Constituicao:
    """Representa a constituição, formada por um conjunto de capítulos.

    Attrs:
        capitulos (list[Capitulo]): Conjunto de capítulos da constituição.
    """

    def __init__(self, xml):
        """Inicia uma instância da classe Constituicao a partir de um documento XML.

        Args:
            xml (Element): Documento XML com o conteúdo da constituição.
        """

        self.capitulos = []

        for capitulo in xml.findall('capitulo'):
            self.capitulos.append(Capitulo(capitulo))

    def gerar_html(self):
        """Gera a materialização da constituição como documento HTML.

        Returns:
            yattag.doc.Doc: Documento HTML com a constituição.
        """

        titulo = 'Constituição da Igreja Presbiteriana do Brasil'

        preambulo = ('Em nome do Pai, do Filho e do Espírito Santo, nós, legítimos representantes '
                     'da Igreja Cristã Presbiteriana do Brasil, reunidos em Supremo Concílio, '
                     'no ano de 1950, com poderes para reforma da Constituição, investidos de toda '
                     'autoridade para cumprir as resoluções da legislatura de 1946, depositando '
                     'toda nossa confiança na bênção do Deus Altíssimo e tendo em vista a promoção '
                     'da paz, disciplina, unidade e edificação do povo de Cristo, elaboramos, '
                     'decretamos e promulgamos, para glória de Deus, a seguinte Constituição da '
                     'Igreja Presbiteriana do Brasil.')

        capitulos = {'preambulo': 'Preâmbulo',
                     'c1': 'I - Natureza, Governo e Fins da Igreja',
                     'c2': 'II - Organização das Comunidades Locais',
                     'c3': 'III - Membros da Igreja',
                     'c4': 'IV - Oficiais',
                     'c5': 'V - Concílios',
                     'c6': 'VI - Comissões e Outras Organizações',
                     'c7': 'VII - Ordens da Igreja',
                     'cdg': 'Disposições Gerais',
                     'cdt': 'Disposições Transitórias'}

        url_css = 'https://cdn.jsdelivr.net/npm/bulma@0.9.1/css/bulma.min.css'

        doc, tag, text, line = Doc().ttl()
        html = {'doc': doc, 'tag': tag, 'text': text, 'line': line}

        doc.asis('<!doctype html>')

        with tag('html', lang='pt-BR', klass='has-navbar-fixed-bottom'):
            with tag('head'):
                doc.stag('meta', charset='utf-8')
                line('title', titulo)
                doc.stag('meta', name='author', content='Igreja Presbiteriana do Brasil')
                doc.stag('meta', name='viewport', content='width=device-width, initial-scale=1')
                doc.stag('link', rel='stylesheet', href=url_css)
                with tag('style'):
                    text('span[data-lang] { font-style: italic; } ')
                    text('del { text-decoration: line-through } ')
                    text('.paragrafo { margin-left: 1rem!important; } ')
                    text('.capitulo, .secao, .artigo, .caput, .paragrafo { margin-bottom: 1.5rem; }')
                line('script', '', src='base.js')

            with tag('body'):
                with tag('nav', ('aria-label', 'main navigation'),
                         klass='navbar is-fixed-bottom is-light is-hidden-mobile'
                         ):
                    with tag('div', klass='navbar-menu'):
                        with tag('div', klass='navbar-start'):
                            with tag('div',
                                     klass='navbar-item has-dropdown has-dropdown-up is-hoverable'):
                                line('a', 'Índice', href='#', klass='navbar-link')

                                with tag('div', klass='navbar-dropdown'):
                                    for chave, texto in capitulos.items():
                                        line('a', texto, klass='navbar-item', href=f'#{chave}')
                                        if chave in ('preambulo', 'c7'):
                                            doc.stag('hr', klass='navbar-divider')

                        with tag('div', klass='navbar-end'):
                            with tag('div', klass='navbar-item'):
                                with tag('label', klass='checkbox'):
                                    doc.stag('input', type='checkbox', id='mostrar_versoes')
                                    text(' Apresentar versões obsoletas')

                with tag('section', klass='section'):
                    with tag('div', klass='container'):
                        line('h1', titulo, klass=CLASSES_TITULO)

                        line('h2', 'Índice', klass=f'{CLASSES_SUBTITULO} is-hidden-tablet')
                        with tag('ul', klass='is-hidden-tablet'):
                            for chave, texto in capitulos.items():
                                with tag('li'):
                                    line('a', texto, href=f'#{chave}')

                        with tag('section', id='preambulo', klass='capitulo'):
                            line('h2', 'Preâmbulo', klass=CLASSES_SUBTITULO)
                            line('p', preambulo)

                        for capitulo in self.capitulos:
                            capitulo.gerar_html(html)

        return doc

    def __str__(self):
        return self.__class__.__name__


class Capitulo:
    """Representa um capítulo da constituição, formado por um conjunto de seções.

    Attrs:
        secoes (list[Secao]): Conjunto de seções do capítulo.
        ide (str): Identificador do capítulo.
        titulo (str): Título do capítulo.
    """

    def __init__(self, xml):
        """Inicia uma instância da classe Capitulo a partir de um fragmento de XML.

        Args:
            xml (Element): Fragmento de XML com o conteúdo do capítulo.
        """

        self.secoes = []
        self.ide = xml.attrib['id']
        self.titulo = xml.attrib['titulo']

        for secao in xml.findall('secao'):
            self.secoes.append(Secao(self, secao))

    def gerar_html(self, html):
        """Adiciona a materialização do capítulo ao documento HTML.

        Args:
            html (dict): Acessórios para materialização.
        """

        tag = html['tag']
        line = html['line']

        with tag('section', id=self.obter_id_html(), klass='capitulo'):
            if self.ide not in ('dg', 'dt'):
                line('h2', f'Capítulo {roman.toRoman(int(self.ide))}', klass=CLASSES_SUBTITULO)

            line('h2', self.titulo, klass=CLASSES_SUBTITULO)

            for secao in self.secoes:
                secao.gerar_html(html)

    def obter_id_html(self):
        """Obtém o identificador do capítulo para uso em link HTML.

        Returns:
            str: Identificador do capítulo.
        """

        return f'c{self.ide}'


class Secao:
    """Representa uma seção de um capítulo, formada por um conjunto de artigos.

    Attrs:
        artigos (list[Artigo]): Conjunto de artigos da seção.
        ide (str): Identificador da seção.
        titulo (str): Título da seção.
        pai (Capitulo): Capítulo que contém a seção.
    """

    def __init__(self, pai, xml):
        """Inicia uma instância da classe Secao a partir de um fragmento de XML.

        Args:
            pai (Capitulo): Capítulo que contém a seção.
            xml (Element): Fragmento de XML com o conteúdo da seção.
        """

        self.artigos = []
        self.ide = int(xml.attrib['id'])
        self.titulo = xml.attrib['titulo'] if 'titulo' in xml.attrib else None
        self.pai = pai

        for artigo in xml.findall('artigo'):
            self.artigos.append(Artigo(artigo))

    def gerar_html(self, html):
        """Adiciona a materialização da seção ao documento HTML.

        Args:
            html (dict): Acessórios para materialização.
        """

        tag = html['tag']
        line = html['line']

        with tag('section', id=self.obter_id_html(), klass='secao'):
            if self.titulo is None:
                titulo = 'Única'
                visibilidade = ' is-sr-only'
            else:
                titulo = f'{self.ide}ª - {self.titulo}'
                visibilidade = ''

            line('h3', f'Seção {titulo}', klass=f'{CLASSES_SECAO}{visibilidade}')

            for artigo in self.artigos:
                artigo.gerar_html(html)

    def obter_id_html(self):
        """Obtém o identificador da seção para uso em link HTML.

        Returns:
            str: Identificador da seção.
        """

        return f'{self.pai.obter_id_html()}_s{self.ide}'


class Artigo:
    """Representa um artigo, formado por um conjunto de parágrafos.

    Attrs:
        paragrafos (list[Paragrafo]): Conjunto de parágrafos do artigo.
        ide (str): Identificador da seção.
    """

    def __init__(self, xml):
        """Inicia uma instância da classe Artigo a partir de um fragmento de XML.

        Args:
            xml (Element): Fragmento de XML com o conteúdo do artigo.
        """

        self.paragrafos = []
        self.ide = int(xml.attrib['id'])

        self.paragrafos.append(Caput(self, xml.find('caput')))

        for paragrafo in xml.findall('paragrafo'):
            self.paragrafos.append(Paragrafo(self, paragrafo))

    def gerar_html(self, html):
        """Adiciona a materialização do artigo ao documento HTML.

        Args:
            html (dict): Acessórios para materialização.
        """

        tag = html['tag']

        with tag('div', id=self.obter_id_html(), klass='artigo'):
            for paragrafo in self.paragrafos:
                paragrafo.gerar_html(html)

    def obter_id_html(self):
        """Obtém o identificador do artigo para uso em link HTML.

        Returns:
            str: Identificador do artigo.
        """

        return f'a{self.ide}'


class Paragrafo:
    """Representa um parágrafo de um artigo.

    Attrs:
        ide (str): Identificador da seção.
        alineas (list[Alineas]): Conjunto de alíneas do parágrafo.
        versoes_texto (list[VersaoTexto]): Conjunto de versões do texto do parágrafo.
        pai (Artigo): Artigo que contém o parágrafo.
    """

    def __init__(self, pai, xml, caput=False):
        """Inicia uma instância da classe Paragrafo a partir de um fragmento de XML.

        Args:
            pai (Artigo): Artigo que contém o parágrafo.
            xml (Element): Fragmento de XML com o conteúdo do parágrafo.
            caput (bool, optional): Valor que indica se o parágrafo é o caput. Padrão: False.
        """

        self.ide = 0 if caput else int(xml.attrib['id'])
        self.alineas = []
        self.versoes_texto = Utilitario.extrair_versoes(xml)
        self.pai = pai

        alineas = xml.find('alineas')

        if alineas is not None:
            for alinea in alineas.findall('alinea'):
                self.alineas.append(Alinea(self, alinea))

    def gerar_html(self, html):
        """Adiciona a materialização do parágrafo ao documento HTML.

        Args:
            html (dict): Acessórios para materialização.
        """

        tag = html['tag']

        if self.ide == 0:
            tipo = 'caput'
            terminal = 'º' if self.pai.ide < 10 else '.'
            rotulo = f'Art. {self.pai.ide}{terminal}'
        else:
            tipo = 'paragrafo'
            if len(self.pai.paragrafos) > 2:
                rotulo = f'§ {self.ide}º.'
            else:
                rotulo = 'Parágrafo único.'

        numero_versoes = len(self.versoes_texto)

        with tag('p', id=self.obter_id_html(), klass=f'{tipo} content'):
            for indice, versao in enumerate(self.versoes_texto, start=1):
                versao_vigente = indice == numero_versoes

                classes = f'versao{"" if versao_vigente else " obsoleta is-hidden"}'

                if versao.instrumento is not None:
                    with tag('span', ('data-instrumento', versao.instrumento), klass=classes):
                        Utilitario.gerar_versao(html, versao_vigente, rotulo, versao.texto)
                else:
                    with tag('span', klass=classes):
                        Utilitario.gerar_versao(html, versao_vigente, rotulo, versao.texto)

            for alinea in self.alineas:
                alinea.gerar_html(html)

    def obter_id_html(self):
        """Obtém o identificador do parágrafo para uso em link HTML.

        Returns:
            str: Identificador do parágrafo.
        """

        return f'{self.pai.obter_id_html()}_p{self.ide}'


class Caput(Paragrafo):
    """Representa o caput de um artigo."""

    def __init__(self, pai, xml):
        """Inicia uma instância da classe Caput a partir de um fragmento de XML.

        Args:
            pai (Artigo): Artigo que contém o caput.
            xml (Element): Fragmento de XML com o conteúdo do caput.
        """

        super().__init__(pai, xml, caput=True)


class Alinea:
    """Representa uma alínea de um parágrafo.

    Attrs:
        ide (str): Identificador da alínea.
        versoes_texto (list[VersaoTexto]): Conjunto de versões do texto da alínea.
        pai (Paragrafo): Parágrafo que contém a alínea.
    """

    def __init__(self, pai, xml):
        """Inicia uma instância da classe Alinea a partir de um fragmento de XML.

        Args:
            pai (Paragrafo): Parágrafo que contém a alínea.
            xml (Element): Fragmento de XML com o conteúdo da alínea.
        """

        self.ide = xml.attrib['id']
        self.versoes_texto = Utilitario.extrair_versoes(xml)
        self.pai = pai

    def gerar_html(self, html):
        """Adiciona a materialização da alínea ao documento HTML.

        Args:
            html (dict): Acessórios para materialização.
        """

        doc = html['doc']
        tag = html['tag']

        doc.stag('br')

        rotulo = f'{self.ide})'
        numero_versoes = len(self.versoes_texto)

        with tag('span', id=self.obter_id_html()):
            for indice, versao in enumerate(self.versoes_texto, start=1):
                versao_vigente = indice == numero_versoes

                classes = f'versao{"" if versao_vigente else " obsoleta is-hidden"}'

                if versao.instrumento is not None:
                    with tag('span', ('data-instrumento', versao.instrumento), klass=classes):
                        Utilitario.gerar_versao(html, versao_vigente, rotulo, versao.texto, False)
                else:
                    with tag('span', klass=classes):
                        Utilitario.gerar_versao(html, versao_vigente, rotulo, versao.texto, False)

    def obter_id_html(self):
        """Obtém o identificador da alínea para uso em link HTML.

        Returns:
            str: Identificador da alínea.
        """

        return f'{self.pai.obter_id_html()}_{self.ide}'


class Utilitario:
    """Define métodos e atributos utilitários para o tratamento da constituição."""

    VersaoTexto = namedtuple('VersaoTexto', 'texto instrumento ordem')

    @staticmethod
    def gerar_versao(html, vigente, rotulo, texto, destacar_rotulo=True):
        """Adiciona a materialização da versão do texto de um item ao documento HTML.

        Args:
            html (dict): Acessórios para materialização.
            vigente (bool): Valor que indica se a versão é vigente.
            rotulo (str): Rótulo do item.
            texto (str): Texto do item na versão.
            destacar_rotulo: Valor que indica se o rótulo deve ser destacado. Padrão: True.
        """

        doc = html['doc']
        tag = html['tag']
        line = html['line']

        if not vigente:
            with tag('del'):
                if destacar_rotulo:
                    line('strong', rotulo)
                    doc.asis(f' {Utilitario.processar_texto(texto)}')
                else:
                    doc.asis(f'{rotulo} {Utilitario.processar_texto(texto)}')

            doc.stag('br')
        else:
            if destacar_rotulo:
                line('strong', rotulo)
                doc.asis(f' {Utilitario.processar_texto(texto)}')
            else:
                doc.asis(f'{rotulo} {Utilitario.processar_texto(texto)}')

    @staticmethod
    def extrair_versoes(xml):
        """Extrai as versões do texto de um item (parágrafo/alínea) a partir de um fragmento de XML.

        Args:
            xml (Element): Fragmento de XML com o texto de um item.

        Returns:
            list[VersaoTexto]: Conjunto de versões do texto de um item.
        """

        versoes = []

        for versao in xml.findall('texto'):
            texto = versao.text
            instrumento = versao.attrib['instrumento'] if 'instrumento' in versao.attrib else None
            ordem = int(versao.attrib['ordem']) if 'ordem' in versao.attrib else 1

            if any(v.ordem == ordem for v in versoes):
                print(f'{ESCAPE_ERRO}Erro{ESCAPE_ENDC}')
                print(f'* Texto com ordem repetida: {texto}')
                sys.exit(1)

            Utilitario.verificar_pontuacao(texto)

            versoes.append(Utilitario.VersaoTexto(texto, instrumento, ordem))

        versoes = sorted(versoes, key=attrgetter('ordem'))

        return versoes

    @staticmethod
    def verificar_pontuacao(texto):
        """Verifica a presença de pontuação ao fim de um texto.

        Args:
            texto (str): Texto que deve terminar com pontuação.
        """

        if not texto.endswith(tuple([';', '.', ':'])):
            print(f'{ESCAPE_ALERTA}Alerta{ESCAPE_ENDC}')
            print(f'* Texto sem terminal: {texto}')

    @staticmethod
    def processar_texto(texto):
        """Processa um texto marcando referências e termos latinos.

        Args:
            texto (str): Texto com referências e termos latinos.

        Returns:
            str: Texto com referências e termos latinos marcados.
        """

        return Utilitario.marcar_referencias(Utilitario.marcar_termos_latinos(texto))

    @staticmethod
    def marcar_referencias(texto):
        """Identifica referências em um texto e as marca como links HTML.

        Args:
            texto (str): Texto com referências.

        Returns:
            str: Texto com referências marcadas.
        """

        return re.sub(r'art\. (\d{1,3})(º)?', r'<a href="#a\1">art. \1\2</a>', texto)

    @staticmethod
    def marcar_termos_latinos(texto):
        """Identifica termos latinos em um texto e os marca para destaque.

        Args:
            texto (str): Texto com termos latinos.

        Returns:
            str: Texto com termos latinos marcados.
        """

        termos = ['ex officio', 'in fine', 'ad referendum', 'quorum']
        return re.sub(f"({'|'.join(termos)})", r'<span data-lang="latim">\1</span>', texto)
