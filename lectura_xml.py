import xml.etree.ElementTree as ET, os


def Charge_Shopping(xml,path):
    # Cargar y parsear el archivo XML
    tree = ET.parse(path+xml)
    root = tree.getroot()

    # Namespace para manejar los prefijos en el XML
    namespaces = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2'
    }

    # Función para obtener el valor de un XPath
    def get_value(xpath):
        element = root.find(xpath, namespaces)
        return element.text if element is not None else 'No disponible'

    # Función para establecer el valor de un XPath
    def set_value(xpath, new_value):
        element = root.find(xpath, namespaces)
        if element is not None:
            element.text = new_value

    # Extraer y actualizar información específica
    descripcion = get_value('.//cbc:Description')

    # Nombre del archivo donde quieres guardar el XML
    file_name = fr'{path}factura.xml'

    # Escribir el contenido en el archivo
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(descripcion)

    # Extraer valores
    def get_values(xpath):
        elements = root.findall(xpath, namespaces)
        return [element.text for element in elements] if elements else ['No disponible']


    try:
        tree = ET.parse(file_name)
        root = tree.getroot()
        # Namespace para manejar los prefijos en el XML
        namespaces = {
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2'
        }

        def format_number(value):
            value_float = float(value)
            return f"{value_float:.2f}".rstrip('0').rstrip('.')

        descripcion = get_values('.//cbc:Description')
        price = get_values('.//cbc:PriceAmount')
        quantity = get_values('.//cbc:BaseQuantity')
        tax = get_values('.//cac:TaxTotal/cbc:TaxAmount')
        ID = get_values('.//cac:StandardItemIdentification/cbc:ID')
        city = get_values('.//cac:AccountingSupplierParty/cac:Party/cac:PhysicalLocation/cac:Address/cbc:CityName')
        precio = get_values('.//cac:TaxTotal/cac:TaxSubtotal/cbc:TaxableAmount')
        total = get_values('.//cac:LegalMonetaryTotal/cbc:PayableAmount')
        fecha = get_values('.//cbc:IssueDate')

        for i in range(len(ID)):
            # Formatear los valores para quitar ceros decimales innecesarios
            formatted_price = format_number(price[i])
            formatted_quantity = format_number(quantity[i])
            formatted_tax = format_number(tax[i])
            formatted_total_factura = format_number(total[0])
            formatted_total_items = format_number(float(price[i]) * float(quantity[i]))

            total_row = format_number((float(price[i]) + float(tax[i])) * float(quantity[i]))
            
            print(f"CODIGO: {ID[i]} - NAME: {descripcion[i]} - Precio: {formatted_price} - Cant: {formatted_quantity} - IVA: {formatted_tax} - Total Item: {formatted_total_items} - Total Row: {total_row} - Total Factura: {formatted_total_factura} - Fecha: {fecha[0]}")

    except ET.ParseError as e:
        print(f"Error al analizar el archivo XML: {e}")
    except FileNotFoundError as e:
        print(f"Archivo no encontrado: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")





# _path = 'C:/laragon/www/asdasdsadasdadsadasd/'
# xml = 'ad00933877540002400002521.xml'
# Charge_Shopping(xml,_path)