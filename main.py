# CODIGO DESARROLLADO POR RAYO-OFC
import requests, re, random, string, base64, binascii, urllib.parse, time, os, sys
from requests_toolbelt import MultipartEncoder
from rich import print as printf
from rich.panel import Panel
from rich.console import Console
from requests.exceptions import RequestException

COOKIE = "PHPSESSID=3qqs59482qg6k1739efj4p3863;"  # Actualiza esto si caduca
HEARTS_ENVIADOS = []
HEARTS_MAXIMOS = 25

class ZefoyTikTok:
    def obtener_formulario(self, url_video: str) -> bool:
        with requests.Session() as sesion:
            sesion.headers.update({
                'Host': 'zefoy.com',
                'User-Agent': 'Mozilla/5.0',
                'Cookie': COOKIE
            })
            try:
                resp = sesion.get('https://zefoy.com/', timeout=10).text
            except RequestException as e:
                printf(f"[bold red]Error al conectar con zefoy.com: {e}")
                return False

            if 'placeholder="Enter Video URL"' in resp:
                nombre_campo = re.search(r'name="(.*?)" placeholder="Enter Video URL"', resp).group(1)
                accion = re.findall(r'action="(.*?)">', resp)[1]
                printf("[bold green]🔎 Formulario de HEARTS encontrado")
                return self.loop_envio_hearts(sesion, nombre_campo, accion, url_video)
            else:
                printf("[bold red]❌ No se encontró formulario de HEARTS")
                return False

    def loop_envio_hearts(self, sesion, nombre_campo: str, accion: str, url_video: str) -> bool:
        enviados = 0
        while enviados < HEARTS_MAXIMOS:
            resultado = self.enviar_peticion(sesion, nombre_campo, accion, url_video)
            if resultado > 0:
                enviados += resultado
                HEARTS_ENVIADOS.append(resultado)
                printf(Panel(f"[bold green]💖 Total enviados: {enviados}/{HEARTS_MAXIMOS}", width=50))
                if enviados >= HEARTS_MAXIMOS:
                    break
            else:
                printf("[bold yellow]⏳ Esperando para reintentar...")

            printf("[bold blue]🕒 Esperando 4 minutos para el próximo envío...\n")
            time.sleep(240)

        return True

    def enviar_peticion(self, sesion, nombre_campo: str, accion: str, url_video: str) -> int:
        limite = '----WebKitFormBoundary' + ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        sesion.headers.update({
            'User-Agent': 'Mozilla/5.0',
            'Cookie': COOKIE,
            'Content-Type': f'multipart/form-data; boundary={limite}'
        })
        datos = MultipartEncoder({nombre_campo: (None, url_video)}, boundary=limite)
        try:
            resp1 = sesion.post(f'https://zefoy.com/{accion}', data=datos, timeout=10).text
        except RequestException as e:
            printf(f"[bold red]Error al enviar URL del video: {e}")
            return 0

        html1 = self.decodificar_base64(resp1)
        if not html1 or 'type="submit"' not in html1:
            return 0

        ocultos = re.findall(r'type="hidden" name="(.*?)" value="(.*?)"', html1)
        if len(ocultos) < 2:
            return 0

        n1, v1 = ocultos[0]
        n2, v2 = ocultos[1]
        siguiente_accion = re.search(r'action="(.*?)"', html1).group(1)
        datos2 = MultipartEncoder({n1: (None, v1), n2: (None, v2)}, boundary=limite)
        try:
            resp2 = sesion.post(f'https://zefoy.com/{siguiente_accion}', data=datos2, timeout=10).text
        except RequestException as e:
            printf(f"[bold red]Error al enviar campos final: {e}")
            return 0

        html2 = self.decodificar_base64(resp2)
        if not html2:
            return 0

        if 'Successfully' in html2 and 'hearts sent' in html2:
            try:
                enviado = int(re.search(r'Successfully (\d+) hearts sent', html2).group(1))
                printf(Panel(f"[bold green]✅ Enviados: +{enviado}", width=50))
                return enviado
            except:
                return 0
        elif 'Checking Timer' in html2:
            printf("[bold yellow]⏳ Temporizador activo. Esperando...")
            return 0
        else:
            printf(f"[bold red]❌ Falló envío de hearts.\n[bold]Respuesta: {html2[:200]}")
            return 0

    def decodificar_base64(self, texto: str) -> str:
        reversed_str = texto[::-1]
        unquoted = urllib.parse.unquote(reversed_str)
        if not re.fullmatch(r'[A-Za-z0-9+/=\s]+', unquoted.strip()):
            return ""
        try:
            dec = base64.b64decode(unquoted)
            return dec.decode('utf-8', errors='ignore')
        except (binascii.Error, UnicodeDecodeError):
            return ""

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    printf(Panel("[bold green]✨ LIKES TIKTOK POWER BY RAYO-OFC V1.1", width=60))
    url = Console().input("[bold white]Ingresa el enlace de TikTok (cuenta NO privada)\n[bold green]>>> ")

    if 'tiktok.com' not in url:
        printf("[bold red]❌ URL no válida. Debe incluir 'tiktok.com'")
        sys.exit(1)

    zendula = ZefoyTikTok()
    try:
        if zendula.obtener_formulario(url):
            printf(f"[bold green]✔️ Envío completado. Total hearts: {sum(map(int, HEARTS_ENVIADOS))}")
        else:
            printf("[bold red]❌ No se pudo completar el envío.")
    except KeyboardInterrupt:
        printf("\n[bold red]⛔ Cancelado por el usuario.")
    except Exception as e:
        printf(f"[bold red]❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()
