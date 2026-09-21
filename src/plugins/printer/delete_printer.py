import cups
import json
from base.plugin.abstract_plugin import AbstractPlugin

class DeletePrinter(AbstractPlugin):
    def __init__(self, data, context):
        super(DeletePrinter, self).__init__()
        self.data = data
        self.context = context
        self.conn = cups.Connection()
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

    def handle_task(self):
        try:
            payload = json.loads(self.data) if isinstance(self.data, (str, bytes)) else self.data
            
            printer_names = payload.get("PRINTER_NAMES", [])

            if not printer_names:
                raise ValueError("Silinecek yazici ismi belirtilmedi.")

            self.logger.info(f"Silme islemi baslatildi. Hedef: {printer_names}")

            success_count = 0
            error_details = []

            for p_name in printer_names:
                try:
                    target_printer = str(p_name).strip()
                    
                    if target_printer:
                        self.conn.deletePrinter(target_printer)
                        success_count += 1
                        self.logger.info(f"Silindi: {target_printer}")
                    
                except Exception as e:
                    self.logger.error(f"Hata ({p_name}): {str(e)}")
                    error_details.append(f"{p_name}: {str(e)}")

            status_msg = f"{success_count} yazici basariyla silindi."
            if error_details:
                status_msg += f" Hatalar: {', '.join(error_details)}"

            message = "İstemcideki yazıcılar başarıyla silindi"

            self.context.create_response(
                code=self.message_code.TASK_PROCESSED.value,
                message=message,
                data=None,
                content_type=self.get_content_type().APPLICATION_JSON.value
            )

        except Exception as e:
            self.logger.error(f"Kritik Silme Hatasi: {str(e)}")
            self.context.create_response(
                code=self.message_code.TASK_ERROR.value,
                message=f"Silme islemi basarisiz: {str(e)}",
                data=None,
                content_type=self.get_content_type().APPLICATION_JSON.value
            )

def handle_task(task, context):
    plugin = DeletePrinter(task, context)
    plugin.handle_task()