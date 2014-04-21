try:
    db = ximport("database")
except:
    db = ximport("__init__")
    reload(db)

book = db.create("book")
book.create_table("pages", ["title", "description", "pagenumber"])

book.pages.append(title="introduction", pagenumber=1)
book.pages.append(title="chapter one", pagenumber=2)
book.pages.append({"title": "chapter two", "pagenumber": 3})

print "Tables created", book.tables()
print "All pages:", book.pages.all()

print book["pages"]

print "Page 1:", book.pages.pagenumber("1")
print "Chapter two:", book.pages.find("*two", key="title")

book.pages.remove(1)
book["pages"].remove(2)
print "Remaining pages:", book.sql("select * from pages")

book.pages.edit(3, pagenumber="appendix")
book.commit()

print book.dump()

book.close()