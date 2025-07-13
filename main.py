# CODIGO DESARROLLADO POR RAYO-OFC
try:
    import requests, re, random, string, base64, urllib.parse, json, time, os, sys
    from requests_toolbelt import MultipartEncoder
    from rich import print as printf
    from PIL import Image
    import pytesseract
    from rich.panel import Panel
    from rich.console import Console
    from requests.exceptions import RequestException
except ModuleNotFoundError as e:
    __import__('sys').exit(f"Error: {str(e).capitalize()}!")

COOKIES, SUKSES, LOGOUT, GAGAL = {
    "Cookie": "PHPSESSID=3qqs59482qg6k1739efj4p3863;"
}, [], [], []

class DIPERLUKAN:
    def __init__(self) -> None:
        pass

    def LOGIN(self) -> bool:
        return True

    def BYPASS_CAPTCHA(self) -> str:
        return ""

    def MENDAPATKAN_FORMULIR(self, video_url: str) -> bool:
        with requests.Session() as session:
            session.headers.update({
                'Host': 'zefoy.com',
                'User-Agent': 'Mozilla/5.0',
                'Cookie': COOKIES["Cookie"]
            })
            try:
                response = session.get('https://zefoy.com/', timeout=10).text
            except RequestException as e:
                printf(f"[bold red]Error al conectar con zefoy.com: {str(e)}")
                return False

            if 'placeholder="Enter Video URL"' in response:
                self.video_form = re.search(r'name="(.*?)" placeholder="Enter Video URL"', response).group(1)
                self.post_action = re.findall(r'action="(.*?)">', response)[1]
                printf("[bold green]Formulario de HEARTS encontrado!")
                time.sleep(1.5)
                self.MENGIRIMKAN_TAMPILAN(self.video_form, self.post_action, video_url)
            else:
                printf("[bold red]Formulario de HEARTS no disponible!")
                COOKIES["Cookie"] = None
                return False

    def MENGIRIMKAN_TAMPILAN(self, video_form: str, post_action: str, video_url: str) -> bool:
        with requests.Session() as session:
            boundary = '----WebKitFormBoundary' + ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            session.headers.update({
                'User-Agent': 'Mozilla/5.0',
                'Cookie': COOKIES["Cookie"],
                'Content-Type': f'multipart/form-data; boundary={boundary}'
            })
            data = MultipartEncoder({video_form: (None, video_url)}, boundary=boundary)
            try:
                response = session.post(f'https://zefoy.com/{post_action}', data=data, timeout=10).text
            except RequestException as e:
                printf(f"[bold red]Error al enviar datos del video: {str(e)}")
                return False

            html = self.DECRYPTION_BASE64(response)
            if not html:
                printf("[bold red]No se pudo decodificar la respuesta base64 del primer paso.")
                return False

            if 'type="submit"' in html:
                fields = re.findall(r'type="hidden" name="(.*?)" value="(.*?)"', html)
                if len(fields) < 2:
                    printf("[bold red]No se pudieron encontrar los campos necesarios.")
                    return False

                video_id_form, video_id = fields[0]
                link_form, link_val = fields[1]
                next_action = re.search(r'action="(.*?)"', html).group(1)

                data2 = MultipartEncoder({
                    video_id_form: (None, video_id),
                    link_form: (None, link_val)
                }, boundary=boundary)

                try:
                    response2 = session.post(f'https://zefoy.com/{next_action}', data=data2, timeout=10).text
                except RequestException as e:
                    printf(f"[bold red]Error al reenviar datos: {str(e)}")
                    return False

                final = self.DECRYPTION_BASE64(response2)
                if not final:
                    printf("[bold red]No se pudo decodificar la respuesta base64 del segundo paso.")
                    return False

                if 'Successfully' in final and 'hearts sent' in final:
                    sent = re.search(r'Successfully (.*?) hearts sent', final).group(1)
                    SUKSES.append(f"{final}")
                    printf(Panel(f"[bold green]Hearts enviados con éxito: +{sent}", width=50))
                    self.MENGIRIMKAN_TAMPILAN(video_form, post_action, video_url)
                elif 'Checking Timer' in final:
                    printf("[bold yellow]Espera unos minutos antes de reenviar.")
                    self.DELAY(0, 60)
                    self.MENGIRIMKAN_TAMPILAN(video_form, post_action, video_url)
                else:
                    printf(f"[bold red]Fallo al enviar hearts.\n[bold]Respuesta: {final}")
                    return False
            else:
                printf("[bold red]Formulario de HEARTS no procesable.")
                return False

    def DECRYPTION_BASE64(self, base64_code: str) -> str:
        try:
            reversed_str = base64_code[::-1]
            unquoted_str = urllib.parse.unquote(reversed_str)
            decoded_bytes = base64.b64decode(unquoted_str)
            return decoded_bytes.decode('utf-8', errors='ignore')  # Ignorar caracteres no ASCII
        except Exception as e:
            printf(f"[bold red]Error al decodificar Base64: {str(e)}")
            return ""

    def DELAY(self, minutes: int, seconds: int) -> None:
        total = minutes * 60 + seconds
        while total:
            mins, secs = divmod(total, 60)
            printf(f"[bold cyan]Esperando: {mins:02d}:{secs:02d}", end='\r')
            time.sleep(1)
            total -= 1

class MAIN:
    def __init__(self):
        self.TAMPILKAN_LOGO()
        printf(Panel("[bold white]Ingresa el enlace de tu video de TikTok (asegúrate de que la cuenta no sea privada)", width=60))
        video_url = Console().input("[bold green]>>> ")

        if 'tiktok.com' in video_url:
            while True:
                try:
                    DIPERLUKAN().MENDAPATKAN_FORMULIR(video_url)
                except KeyboardInterrupt:
                    printf("\n[bold red]Cancelado por el usuario.")
                    break
                except Exception as e:
                    printf(f"[bold red]Error inesperado: {str(e)}")
        else:
            printf("[bold red]URL no válida. Debe ser un enlace de TikTok.")
            sys.exit()

    def TAMPILKAN_LOGO(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        printf(Panel("[bold green]LIKES TIKTOK POWER BY RAYO-OFC V1.0", width=60))

if __name__ == "__main__":
    MAIN()
