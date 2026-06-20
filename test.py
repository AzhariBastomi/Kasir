import usb.core
for dev in usb.core.find(find_all=True):
    try:
        print(hex(dev.idVendor), hex(dev.idProduct), dev.product)
    except Exception as e:
        print("Error:", e)