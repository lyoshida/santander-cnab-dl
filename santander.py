import enum
import logging
import os
import re

import selenium
from config import LOGIN_URL, BASE_URL, CHROMEDRIVER_PATH, DOWNLOAD_FOLDER
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class MainMenu(enum.Enum):
    CONTA_CORRENTE = 0
    COBRANCA_E_RECEBIMENTOS = 1
    TRANSFERENCIA_DE_ARQUIVOS = 2


class CobrancaMenu(enum.Enum):
    RESUMO_POSICAO = 0
    LANCAMENTOS_CC = 1
    TITULOS = 2
    TITULOS_REJEITADOS = 3
    CONSOLIDACAO = 4
    LIQUIDACAO_BANCO_CORRESPONDENTE = 5
    AVISO_MOVIMENTACAO = 6
    POSICAO_DE_CARTEIRA_CENTRALIZADORA = 7
    FLUXO_DE_RECEBIMENTO = 8
    LIQUIDACOES_POR_CENTRALIZADORA = 9


class TransferenciaArquivosMenu(enum.Enum):
    HISTORICO_TRANSMISSOES = 1
    CONSULTAR = 3


def enable_download_in_headless_chrome(driver, download_dir: str = DOWNLOAD_FOLDER):
    # add missing support for chrome "send_command"  to selenium webdriver
    logger.info('enabling download in chrome headless...')
    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')

    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
    command_result = driver.execute("send_command", params)

    logger.info("response from browser:")
    for key in command_result:
        logger.info("result:" + key + ":" + str(command_result[key]))


class Santander:
    """
    :raises selenium.common.exceptions.WebDriverException: when chromedriver is not found
    """

    def __init__(self,
                 agencia: str,
                 conta: str,
                 user: str,
                 senha: str,
                 cnab_date: str,
                 login_url: str = LOGIN_URL,
                 base_url: str = BASE_URL,
                 chromedriver_path: str = CHROMEDRIVER_PATH):

        print('Assigning variables')
        self.agencia = agencia
        self.conta = conta
        self.user = user
        self.senha = senha
        self.cnab_date = cnab_date
        self.login_url = login_url
        self.base_url = base_url
        self.chromedriver_path = chromedriver_path

        print('chrome options start')
        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {
            "profile.default_content_settings.popups": 0,
            "download.default_directory": DOWNLOAD_FOLDER,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True
        })
        options.add_argument('download.default_directory={}'.format(DOWNLOAD_FOLDER))
        options.add_argument('download.prompt_for_download=false')
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--window-size=1280x1696')
        options.add_argument('--user-data-dir=/tmp/user-data')
        options.add_argument('--hide-scrollbars')
        options.add_argument('--enable-logging')
        options.add_argument('--log-level=0')
        options.add_argument('--v=99')
        options.add_argument('--single-process')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--data-path=/tmp/data-path')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--homedir=/tmp/')
        options.add_argument('--disk-cache-dir=/tmp/cache-dir')
        options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
        options.binary_location = os.getcwd() + "/bin/headless-chromium"
        print('chrome options end')
        print(self.chromedriver_path)
        print('instantiating chromedriver')
        self.driver = webdriver.Chrome(options=options)

        enable_download_in_headless_chrome(self.driver)

    def _change_to_frame_context(self):
        """
        Need to to change to this context to access Agencia/Conta and User/Password forms
        """
        self.driver.switch_to.frame(self.driver.find_elements_by_tag_name('iframe')[0])
        frameset = self.driver.find_element_by_id('frmSet')
        frame = frameset.find_elements_by_tag_name('frame')[2]
        self.driver.switch_to.frame(frame)

    def login(self):

        print('Opening login page {}'.format(self.login_url))
        self.driver.get(self.login_url)

        print('Switching login context')
        self._change_to_frame_context()

        agencia_input = self.driver.find_element_by_id('txtAgencia')
        conta_input = self.driver.find_element_by_id('txtConta')

        print('Filling agencia {}'.format(self.agencia))
        agencia_input.send_keys(self.agencia)
        print('Filling conta {}'.format(self.conta))
        conta_input.send_keys(self.conta)

        print('Clicking OK')
        ok_btn = self.driver.find_element_by_tag_name('a')
        ok_btn.click()

        self.driver.implicitly_wait(3)

        self.driver.switch_to.default_content()
        self._change_to_frame_context()

        nome_input = self.driver.find_element_by_xpath('//input[@name="txtNome"]')
        senha_input = self.driver.find_element_by_xpath('//input[@name="txtSenha"]')

        print('Filling user {}'.format(self.user))
        nome_input.send_keys(self.user)

        print('Filling password {}'.format(''.join(['*' for i in self.senha])))
        senha_input.send_keys(self.senha)
        senha_input.send_keys(Keys.RETURN)

        self.driver.implicitly_wait(3)

    def _check_text_exists(self, text: str) -> bool:

        src = self.driver.page_source
        return bool(re.search(text, src))

    def click_main_menu(self, key: MainMenu) -> None:
        self.driver.get('{}/ibeweb/pages/home/homeNovo.xhtml'.format(self.base_url))
        self.driver.implicitly_wait(3)
        link = self.driver.find_element_by_xpath('//*[@id="formGeral:j_id_5z"]/ul/li[{}]/a'.format(key.value))
        link.click()
        self.driver.implicitly_wait(3)

    def click_cobranca_section_link(self, key: CobrancaMenu) -> None:
        """
        1: Resumo / Posição
        2: Lançamentos C/C
        3: Títulos
        4: Títulos Rejeitados
        5: Consolidação
        6: Liquidação Banco Correspondente
        7: Aviso Movimentação
        8: Posição de Carteira Centralizadora
        9: Fluxo de Recebimento
        10: Liquidações por Centralizadora

        :param key: The key according to the list above
        :return: None
        """

        element_id = 'formGeral:j_id_7z:{}:j_id_84'.format(key.value)
        self.driver.find_element_by_id(element_id).click()
        self.driver.implicitly_wait(3)

        # TODO: Need to remove the pop up

    def click_transferencia_arquivos_section_link(self, key: TransferenciaArquivosMenu) -> None:
        """
        1: Histórico de Transmissões
        3: Consultar
        """
        self.driver.find_element_by_xpath('//*[@id="formGeral:j_id_77:{}:j_id_7c"]'.format(key.value)).click()
        self.driver.implicitly_wait(3)

        # //*[@id="formGeral:j_id_77:3:j_id_7c"]
        # //*[@id="formGeral:j_id_7i:3:j_id_7n"]

    def click_produto_select(self, option_name: str):
        """
        Select produto 'Cobrança' on Transferência de Arquivos -> Retorno
        """
        self.driver.switch_to.default_content()
        iframe = self.driver.find_element_by_xpath('//*[@id="Principal"]')
        self.driver.switch_to.frame(iframe)
        frame = self.driver.find_element_by_xpath('//*[@id="frmSet"]/frame[3]')
        self.driver.switch_to.frame(frame)
        iframe = self.driver.find_element_by_xpath('//*[@id="iframePrinc"]')
        self.driver.switch_to.frame(iframe)
        frame = self.driver.find_element_by_xpath('/html/frameset/frame[1]')
        self.driver.switch_to.frame(frame)
        product_select = Select(self.driver.find_element_by_xpath('//*[@id="cboProduto"]'))
        product_select.select_by_visible_text(option_name)

    def click_layout_select(self, option_name: str):
        """
        Select layout 'Cobrança' on Transferência de Arquivos -> Retorno
        """
        self.driver.switch_to.default_content()
        iframe = self.driver.find_element_by_xpath('//*[@id="Principal"]')
        self.driver.switch_to.frame(iframe)
        frame = self.driver.find_element_by_xpath('//*[@id="frmSet"]/frame[3]')
        self.driver.switch_to.frame(frame)
        iframe = self.driver.find_element_by_xpath('//*[@id="iframePrinc"]')
        self.driver.switch_to.frame(iframe)
        layout_select = Select(self.driver.find_element_by_xpath('//*[@id="slcProdRet"]'))
        layout_select.select_by_visible_text(option_name)

    def click_outros_periodos(self):
        """
        Select Outros períodos
        """
        self.driver.switch_to.default_content()
        iframe = self.driver.find_element_by_xpath('//*[@id="Principal"]')
        self.driver.switch_to.frame(iframe)
        frame = self.driver.find_element_by_xpath('//*[@id="frmSet"]/frame[3]')
        self.driver.switch_to.frame(frame)
        iframe = self.driver.find_element_by_xpath('//*[@id="iframePrinc"]')
        self.driver.switch_to.frame(iframe)
        self.driver.find_element_by_xpath('//*[@id="lnkOutrosPeriodos"]').click()

    def set_date_ranges(self, start_date: str, end_date: str):

        self.driver.switch_to.default_content()
        iframe = self.driver.find_element_by_xpath('//*[@id="Principal"]')
        self.driver.switch_to.frame(iframe)
        frame = self.driver.find_element_by_xpath('//*[@id="frmSet"]/frame[3]')
        self.driver.switch_to.frame(frame)
        iframe = self.driver.find_element_by_xpath('//*[@id="iframePrinc"]')
        self.driver.switch_to.frame(iframe)

        self.driver.find_element_by_xpath('//*[@id="txtData"]').send_keys(Keys.BACKSPACE * 11)
        self.driver.find_element_by_xpath('//*[@id="txtData1"]').send_keys(Keys.BACKSPACE * 11)
        self.driver.find_element_by_xpath('//*[@id="txtData"]').send_keys(start_date)
        self.driver.find_element_by_xpath('//*[@id="txtData1"]').send_keys(end_date)

        self.driver.find_element_by_xpath('//*[@id="divOutroPeriodo"]/div/table/tbody/tr[2]/td[2]/a').click()

    def get_files(self):

        self.driver.switch_to.default_content()
        iframe = self.driver.find_element_by_xpath('//*[@id="Principal"]')
        self.driver.switch_to.frame(iframe)
        frame = self.driver.find_element_by_xpath('//*[@id="frmSet"]/frame[3]')
        self.driver.switch_to.frame(frame)
        iframe = self.driver.find_element_by_xpath('//*[@id="iframePrinc"]')
        self.driver.switch_to.frame(iframe)

        error = False
        row = 0
        while not error:
            try:
                lista = self.driver.find_element_by_id('divArqsRet')
                table_row = lista.find_element_by_id('lin{}'.format(row))
                col = table_row.find_element_by_css_selector('td:nth-child(3)')
                filename = col.text
                logger.info('Found file: {}'.format(filename))

                if 'MOV' in filename:
                    logger.info('Clicking to download file {}'.format(filename))
                    self.driver.find_element_by_xpath('//*[@id="lin{}"]/td[8]/a'.format(row)).click()
            except selenium.common.exceptions.NoSuchElementException:
                error = True
            row += 1

        self.driver.get('https://unsplash.com/photos/aFYkD-ggewc/download?force=true')
