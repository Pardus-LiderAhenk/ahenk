import cups
import json
from base.plugin.abstract_plugin import AbstractPlugin

class GetPrinters(AbstractPlugin):
    def __init__(self, data, context):
        super(GetPrinters, self).__init__()
        self.data = data
        self.context = context
        self.conn = cups.Connection()
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

    def handle_task(self):
        try:
            printers = self.conn.getPrinters()
            printer_list = []

            for name, info in printers.items():
                printer_list.append({
                    "PRINTER_NAME": str(name),
                    "DEVICE_URI": str(info.get("device-uri", "")),
                    "PPD_NAME": str(info.get("printer-make-and-model", "")),
                    "DESCRIPTION": str(info.get("printer-info", "")),
                    "LOCATION": str(info.get("printer-location", "")),
                    "STATE": str(info.get("printer-state", ""))
                })

            result_json = json.dumps({"PRINTER_LIST": printer_list})
            
            self.logger.debug(f"Websocket üzerinden gönderiliyor: {result_json}")

            self.context.create_response(
                code=self.message_code.TASK_PROCESSED.value,
                message="Kayıtlı yazıcılar getirildi",
                data=result_json ,
                content_type=self.get_content_type().APPLICATION_JSON.value
            )

        except Exception as e:
            self.logger.error(f"Hata: {str(e)}")
            self.context.create_response(
                code=self.message_code.TASK_ERROR.value,
                message=f"Hata: {str(e)}",
                data=None
            )

def handle_task(task, context):
    plugin = GetPrinters(task, context)
    plugin.handle_task()