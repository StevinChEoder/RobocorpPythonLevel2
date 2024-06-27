from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF 
from RPA.Archive import Archive

@task

def order_robots_from_RobotSpareBin():

    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """

    """browser.configure(
        slowmo=1000
    )"""

    #archive_receipts()

    open_robot_order_website()

    download_orders_file()

    orders = get_orders()

    #fill_the_form()

    for order in orders:
        fill_the_form(order)

    archive_receipts()

def open_robot_order_website():

    """Opens the website to order the robots"""

    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def download_orders_file():

    """Downloads the orders file from the website"""

    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def get_orders():

    """Reads the downloaded csv file as a table and puts it into a variable"""

    tables = Tables()
    orders = tables.read_table_from_csv("orders.csv")
    return orders

def close_annoying_modal():
    page = browser.page()
    page.click("button:text('OK')")

def fill_the_form(order):
    close_annoying_modal()
    page = browser.page()
    page.select_option("#head", order['Head'] ) 
    radio_button_xpath = "//div[@class='radio form-check']//input[@value="+order['Body']+"]"
    page.click(radio_button_xpath)
    legs_field_xpath = "//input[@placeholder='Enter the part number for the legs']"
    page.fill(legs_field_xpath, order['Legs'])
    page.fill("#address", order['Address'])
    page.click("#preview")
    page.click("#order")
    alert_message_xpath = "//div[@class='alert alert-danger']"
    while(page.is_visible(alert_message_xpath)):
        page.click("#order")
    
    pdf_file_path = store_receipt_as_pdf(order['Order number'])
    screenshot_file_path = take_order_screenshot(order['Order number'])

    list_of_files = [screenshot_file_path]
    pdf = PDF()
    pdf.add_files_to_pdf(files=list_of_files, target_document=pdf_file_path, append = True)

    page.click("#order-another")

def store_receipt_as_pdf(orderno):
    page = browser.page()
    order_receipt_html = page.locator("#receipt").inner_html()
    pdf_file_path = "output/order_receipts/"+orderno+".pdf"

    pdf = PDF()
    pdf.html_to_pdf(order_receipt_html,pdf_file_path)
    return pdf_file_path

def take_order_screenshot(orderno):
    page = browser.page()
    screenshot_file_path = "output/order_screenshots/"+orderno+".png"
    locator = page.locator("#robot-preview-image")
    page.screenshot(path=screenshot_file_path, omit_background=True)
    return(screenshot_file_path)

def archive_receipts():
    archive = Archive()
    archive.archive_folder_with_zip(folder="output/order_receipts",archive_name="output/order_receipts.zip")