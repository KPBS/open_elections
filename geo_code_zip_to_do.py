def geocode_zip():
    # TODO: change this code to use
    # http://www.zip-codes.com/zip-code/91902/zip-code-91902.asp and
    # BeautifulSoup
    import requests
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("""SELECT DISTINCT
            tran_zip
        FROM
            open_elections_contribution
        WHERE
            CHAR_LENGTH(tran_zip)> 2
            AND tran_zip != '00000'
            AND tran_zip NOT IN (SELECT zip_code from open_elections_contributionzipcode)
        ORDER BY
            tran_zip""")

    for row in cursor.fetchall():
        zip = str(row[0])
        url = 'http://geocoder.us/service/csv/geocode?zip=%s' % zip
        # print "url = %s\n" % url
        r = requests.get(url)
        codes = r.text.split(', ')
        try:
            c = ContributionZipCode(
                    latitude=codes[0][:7],
                    longitude=codes[1][:7],
                    zip_code=codes[4])
            c.save()
        except:
            pass
