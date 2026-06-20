from escpos.printer import Usb

p = Usb(0x0fe6, 0x811e, 0, in_ep=0x81, out_ep=0x01)
p.text("Tes print dari Raspberry Pi\n")
p.cut()