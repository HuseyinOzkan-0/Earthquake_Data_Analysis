from app import scrape_kandilli, app

if __name__ == '__main__':
    with app.app_context():
        df = scrape_kandilli()
        print('Scrape returned rows:', len(df))
