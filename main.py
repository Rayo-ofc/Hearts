# CODIGO DESARROLLADO POR RAYO-OFC
try:
    import requests, re, random, string, base64, binascii, urllib.parse, time, os, sys
    from requests_toolbelt import MultipartEncoder
    from rich import print as printf
    from rich.panel import Panel
    from rich.console import Console
    from requests.exceptions import RequestException
except ModuleNotFoundError as e:
    sys.exit(f"Error: {str(e).capitalize()}!")

COOKIE = "PHPSESSID=3qqs59482qg6k1739efj4p3863;"
HEARTS_ENVIADOS = []

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
                time.sleep(1)
                return self.enviar_peticion(nombre_campo, accion, url_video)
            else:
                printf("[bold red]❌ No se encontró formulario de HEARTS")
                return False

    def enviar_peticion(self, nombre_campo: str, accion: str, url_video: str) -> bool:
        with requests.Session() as sesion:
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
                return False

            html1 = self.decodificar_base64(resp1)
            if not html1:
                printf("[bold red]❌ Falló decodificación base64 paso 1")
                return False

            if 'type="submit"' in html1:
                ocultos = re.findall(r'type="hidden" name="(.*?)" value="(.*?)"', html1)
                if len(ocultos) < 2:
                    printf("[bold red]❌ No se encontraron los campos hidden necesarios")
                    return False

                n1, v1 = ocultos[0]
                n2, v2 = ocultos[1]
                siguiente_accion = re.search(r'action="(.*?)"', html1).group(1)

                datos2 = MultipartEncoder({n1: (None, v1), n2: (None, v2)}, boundary=limite)
                try:
                    resp2 = sesion.post(f'https://zefoy.com/{siguiente_accion}', data=datos2, timeout=10).text
                except RequestException as e:
                    printf(f"[bold red]Error al enviar campos final: {e}")
                    return False

                html2 = self.decodificar_base64(resp2)
                if not html2:
                    printf("[bold red]❌ Falló decodificación base64 paso 2")
                    return False

                if 'Successfully' in html2 and 'hearts sent' in html2:
                    enviado = re.search(r'Successfully (.*?) hearts sent', html2).group(1)
                    HEARTS_ENVIADOS.append(enviado)
                    printf(Panel(f"[bold green]✅ Hearts enviados: +{enviado}", width=50))
                    return True
                elif 'Checking Timer' in html2:
                    printf("[bold yellow]⏳ Espera unos segundos antes de reintentar.")
                    time.sleep(60)
                    return self.enviar_peticion(nombre_campo, accion, url_video)
                else:
                    printf(f"[bold red]❌ Falló envío de hearts.\n[bold]Respuesta: {html2}")
                    return False
            else:
                printf("[bold red]❌ Formulario de HEARTS no procesable en paso 1")
                return False

    def decodificar_base64(self, texto: str) -> str:
        reversed_str = texto[::-1]
        unquoted = urllib.parse.unquote(reversed_str)
        if not re.fullmatch(r'[A-Za-z0-9+/=\s]+', unquoted):
            printf("[bold yellow]⚠️ Advertencia: contenido recibido no es base64 válido.")
            printf(Panel(unquoted[:500], title="Contenido recibido", width=80))
            return ""
        try:
            dec = base64.b64decode(unquoted)
            return dec.decode('utf-8', errors='ignore')
        except (binascii.Error, UnicodeDecodeError) as e:
            printf(f"[bold red]Error decodificando Base64: {e}")
            printf(Panel(unquoted[:500], title="Contenido recibido (recortado)", width=80))
            return ""

def main():
    os.system('cls' if os.name=='nt' else 'clear')
    printf(Panel("[bold green]✨ LIKES TIKTOK POWER BY RAYO-OFC V1.0", width=60))
    printf(Panel("[bold white]Ingresa el enlace de TikTok (cuenta NO privada)", width=60))
    url = Console().input("[bold green]>>> ")
    if 'tiktok.com' not in url:
        printf("[bold red]❌ URL no válida. Debe incluir 'tiktok.com'")
        sys.exit(1)

    zendula = ZefoyTikTok()
    try:
        if zendula.obtener_formulario(url):
            printf(f"[bold green]✔️ Operación finalizada. Hearts enviados: {HEARTS_ENVIADOS}")
        else:
            printf("[bold red]❌ La operación no pudo completarse.")
    except KeyboardInterrupt:
        printf("\n[bold red]📛 Terminado por el usuario.")
    except Exception as e:
        printf(f"[bold red]❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()
