import json
import cups
from base.plugin.abstract_plugin import AbstractPlugin

class AddPrinter(AbstractPlugin):
    def __init__(self, data, context):
        super(AddPrinter, self).__init__()
        self.data = data
        self.context = context
        self.conn = cups.Connection()
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

    def handle_task(self):
        try:
            payload = self.data
            if isinstance(payload, (str, bytes)):
                payload = json.loads(payload)

            printer_list = payload.get("PRINTER_LIST")

            if not printer_list:
                self.logger.error(f"PRINTER_LIST anahtari bulunamadi. Mevcut: {list(payload.keys())}")
                raise ValueError("Yazici listesi bos veya gecersiz.")

            success_count = 0
            error_details = []

            for printer in printer_list:
                p_name = printer.get("printerName") or printer.get("PRINTER_NAME")
                p_uri = printer.get("deviceUri") or printer.get("DEVICE_URI")
                ppd_to_use = printer.get("ppdName") or printer.get("PPD_NAME") or "raw"
                description = printer.get("description") or printer.get("DESCRIPTION") or ""
                location = printer.get("location") or printer.get("LOCATION") or ""
                
                if not p_name or not p_uri:
                    continue

                try:
                    # CUPS İşlemi
                    self.conn.addPrinter(
                        name=str(p_name),
                        device=str(p_uri),
                        ppdname=str(ppd_to_use),
                        info=str(description),
                        location=str(location)
                    )
                    self.conn.enablePrinter(p_name)
                    self.conn.acceptJobs(p_name)

                    # Default Ayarı
                    set_default = printer.get("setDefault") or printer.get("SET_DEFAULT")
                    if str(set_default).lower() in ("true", "1", "yes"):
                        self.conn.setDefault(p_name)
                    
                    success_count += 1
                    self.logger.info(f"Yazici eklendi: {p_name}")

                except Exception as e:
                    self.logger.error(f"Yazici hatasi ({p_name}): {str(e)}")
                    error_details.append(f"{p_name}: {str(e)}")

            self._send_response(success_count, len(printer_list), error_details)

        except Exception as e:
            self.logger.error(f"Kritik Hata: {str(e)}")
            self.context.create_response(
                code=self.message_code.TASK_ERROR.value,
                message=f"Kritik Hata: {str(e)}",
                data=None,
                content_type=self.get_content_type().APPLICATION_JSON.value
            )

    def _send_response(self, success, total, errors):
        if success == total:
            code = self.message_code.TASK_PROCESSED.value
            msg = "Yazicilar basariyla eklendi."
        elif success > 0:
            code = self.message_code.TASK_WARNING.value
            msg = f"Kismen basarili ({success}/{total})."
        else:
            code = self.message_code.TASK_ERROR.value
            msg = "Ekleme basarisiz."

        self.context.create_response(
            code=code,
            message=msg,
            data=json.dumps({"errors": errors}),
            content_type=self.get_content_type().APPLICATION_JSON.value
        )

def handle_task(task, context):
    plugin = AddPrinter(task, context)
    plugin.handle_task()