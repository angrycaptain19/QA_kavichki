from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import sqlite3


def test_setup():
        global driver
        driver = webdriver.Chrome(executable_path="./drivers/chromedriver.exe")
        driver.maximize_window()
        driver.get('https://checkme.kavichki.com/')
        driver.implicitly_wait(3)
        # Подключение к БД
        global conn, c
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        # Сбор заголовков таблицы
        headers_data = []
        headers = driver.find_elements(By.XPATH, '//table/thead/tr/th')
        for x in range(1, len(headers) + 1):
            header = driver.find_element(By.XPATH, '//table/thead/tr/th[' + str(x) + ']').text
            headers_data.append(header)

        # Сбор данных таблицы
        global table_data
        table_data = []
        row = driver.find_elements(By.XPATH, '//table/tbody/tr[1]/td')
        column = driver.find_elements(By.XPATH, '//table/tbody/tr/td[1]')
        for rows in range(1, len(row) + 1):
            for columns in range(1, len(column) + 1):
                table = driver.find_element(By.XPATH,
                                            '//table/tbody/tr[' + str(rows) + ']/td[' + str(columns) + ']').text
                table_data.append(table)

        # Создание того же формата данных, что будет в БД
        global google_rows
        google_rows = [table_data[i:i + 4] for i in range(0, len(table_data), 4)]
        for x in range(len(google_rows)):
            google_rows[x].remove('Удалить')
        google_rows = [tuple(x) for x in google_rows]

        # Создание таблицы
        c.execute("CREATE TABLE buylist (" + headers_data[0].replace(' ', '_') + " TEXT," + headers_data[1] + " TEXT,"
                  + headers_data[2].replace(', ', '_') + " TEXT)")

        # Вставка данных в таблицу
        rows = [table_data[i:i + 4] for i in range(0, len(table_data), 4)]
        for x in range(len(rows)):
            c.execute("INSERT INTO buylist VALUES ('" + rows[x][0] + "', '" + rows[x][1] + "', '" + rows[x][2] + "')")
            conn.commit()

def test_compare_tables():
        # Просмотр данных таблицы
        global db_rows
        c.execute("SELECT * FROM buylist")
        db_rows = c.fetchall()
        assert db_rows == google_rows


def test_add_new_row():
        # Добавление нового поля в таблицу
        driver.find_element(By.XPATH, "//html/body/a[@id='open']").click()
        driver.find_element(By.ID, 'name').send_keys('Батарейки')
        driver.find_element(By.ID, 'count').send_keys('10')
        driver.find_element(By.ID, 'price').send_keys('1500')
        driver.find_element(By.ID, 'add').click()
        assert 'Батарейки' in driver.find_element(By.XPATH, '//tbody/tr[5]/td[1]').text
        assert '1500' in driver.find_element(By.XPATH, '//tbody/tr[5]/td[2]').text
        assert '10' in driver.find_element(By.XPATH, '//tbody/tr[5]/td[3]').text
        # Сбор измененных данных
        table_data.clear()
        rows = driver.find_elements(By.XPATH, '//table/tbody/tr/td[1]')
        columns = driver.find_elements(By.XPATH, '//table/tbody/tr[1]/td')
        for row in range(1, len(rows) + 1):
            for column in range(1, 4):
                new_table = driver.find_element(By.XPATH,
                                                '//table/tbody/tr[' + str(row) + ']/td[' + str(column) + ']').text
                table_data.append(new_table)
        global google_rows
        google_rows = [table_data[i:i + 3] for i in range(0, len(table_data), 3)]
        google_rows = [tuple(x) for x in google_rows]


def test_clear_button():
        driver.find_element(By.XPATH, '/html/body/a[2]').click()
        assert driver.find_element(By.XPATH, '//tbody/tr[5]/td[1]').text == ''
        assert driver.find_element(By.XPATH, '//tbody/tr[5]/td[2]').text == ''
        assert driver.find_element(By.XPATH, '//tbody/tr[5]/td[3]').text == ''


def test_check_sitetable():
        if google_rows == db_rows:
            print('Данные таблицы на сайте совпадают с данными таблицы в БД')
            assert google_rows == db_rows
        else:
            diff = set(google_rows) - set(db_rows)
            print('Обнаружено отличие от данных в таблице buylist: ' + str(diff))
            assert google_rows == db_rows


def test_delete_row():
        try:
            driver.find_element(By.XPATH, "//tbody/tr[5]/td[4]/a[@class='delete']")
        except NoSuchElementException:
            print('Строка успешно удалена')
            return False


def test_shutdown():
        # Закрытие подключения к БД
        conn.close()
        # Закрытие браузера
        driver.close()
        driver.quit()
