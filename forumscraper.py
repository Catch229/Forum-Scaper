import mechanicalsoup
import re
import time
import csv
import string
import os.path

br = mechanicalsoup.StatefulBrowser(
        soup_config={'features': 'lxml'},
        raise_on_404=True,
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0',
)

pageRegex = re.compile("\/ (\d+)")


def write_csv(file, data):
    if os.path.exists(file):
        f = open(file,"a", encoding="utf-8")
    else:
        f = open(file, "w", encoding="utf-8")
        headers = "author,time,link,image,data\n"
        f.write(headers)

    f.write(",".join(data) + "\n")
    f.close()


def collect_posts():
    first_housing = br.open("https://saesrpg.uk/category/192/inactive-requests-archive")

    pages = first_housing.soup.find_all("li", class_="page select-page")

    num_pages = pageRegex.search(str(pages[1]))

    print("Max page #: " + num_pages.group(1))

    filename = "posts.csv"
    f = open(filename, "w", encoding="utf-8")

    headers = "index,link,author,date\n"

    f.write(headers)

    for p in range(1, int(num_pages.group(1)) + 1):
        current_page = br.open("https://saesrpg.uk/category/192/inactive-requests-archive?page=" + str(p))
        print("Collecting Post URLs from page " + str(p) + "...")
        posts = current_page.soup.find_all("li", class_="clearfix category-item zebra locked")
        for c in posts:
            print(c.find("span", class_="timeago"))
            data = str(p) + "," \
                   + c.find("a", itemprop="url")["href"] + "," \
                   + c.find("div", class_="avatar")["title"] + "," \
                   + c.find("span", class_="timeago")["title"] + "\n"
            f.write(data)
        time.sleep(0.25)

    f.close()


def collect_post_data(csv_file):

    with open(csv_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        i = 0
        #print(reader)
        for row in reader:
            post_image = ''
            i += 1
            print(i)
            current_page = br.open("https://saesrpg.uk"+row['link'])
            post = current_page.soup.find_all("div", component="post/content")
            post_text = post[0].find("p")
            if post_text:
                post_text = post_text.getText()
            else:
                post_text = " "
            link_hyper = post[0].find(href=re.compile("^https://"))
            link_image = post[0].find(src=re.compile("^https://"))
            if link_hyper is None and link_image is None:
                print("Image not found")
            elif link_image is None:
                post_image = link_hyper['href']
            else:
                post_image = link_image['src']

            post_text = post_text.lower().strip().replace(":", " ")
            post_text = post_text.translate(str.maketrans('', '', string.punctuation))
            post_data = ' '.join(post_text.split())

            post_author = current_page.soup.find_all("a", itemprop="author")[0]["data-username"]

            post_date = current_page.soup.find_all("meta", itemprop="datePublished")[0]["content"]
            post_date = re.search("\d+-\d+-\d+", post_date).group()

            write_csv("postdata.csv", [post_author, post_date, row['link'], post_image, post_data])

            time.sleep(0.25)

def collect_users():
    first_user_page = br.open("https://saesrpg.uk/users")

    pages = first_user_page.soup.find_all("li", class_="page select-page")

    num_pages = pageRegex.search(str(pages[1]))

    print("Max page #: " + num_pages.group(1))

    filename = "users.csv"
    f = open(filename, "w", encoding="utf-8")

    headers = "uid,username,last seen,link\n"

    f.write(headers)

    for p in range(1, int(num_pages.group(1)) + 1):
        current_page = br.open("https://saesrpg.uk/users?page=" + str(p))
        print("Collecting User URLs from page " + str(p) + "...")
        users = current_page.soup.find_all("li", class_="users-box registered-user")
        for c in users:
            current_page = br.open("https://saesrpg.uk"+c.find("span", class_="user-name").find("a")["href"])
            last_online = current_page.soup.find(string="Last Online").parent.parent.parent.find("strong")["title"]
            last_online = re.search("\d+-\d+-\d+", last_online).group()
            data = c["data-uid"] + "," \
                   + c.find("span", class_="user-name").find("a").getText() + "," \
                   + last_online + "," \
                   + c.find("span", class_="user-name").find("a")["href"] + "\n"
            f.write(data)
            print(data)
        time.sleep(0.25)

    f.close()


if __name__ == "__main__":

    url = 'https://saesrpg.uk/login'

    username = "Catch22"
    password = "111111"

    login_page = br.open(url)

    login_form = br.select_form()

    br["username"] = username
    br["password"] = password

    response = br.submit_selected()

    #collect_posts()

    #collect_post_data("posts.csv")

    collect_users()



