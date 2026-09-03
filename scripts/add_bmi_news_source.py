from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
url='https://rolunk.at/tag/becsi-magyar-iskola/'
if url not in s:
    # Add BMI news link next to the Központi news link in the news/press section if present
    anchor='https://rolunk.at/tag/kozponti-szovetseg/'
    if anchor in s:
        marker='<a href="https://rolunk.at/tag/kozponti-szovetseg/"'
        i=s.find(marker)
        if i!=-1:
            end=s.find('</a>',i)
            if end!=-1:
                end+=4
                addition=' <a href="https://rolunk.at/tag/becsi-magyar-iskola/" target="_blank" rel="noopener">Bécsi Magyar Iskola – hírek a Rólunk.at-on ↗</a>'
                s=s[:end]+addition+s[end:]
    # If no press block anchor was found, append a compact official press card before footer/main end
    if url not in s:
        block='''\n<section class="section alt" id="hirek-bmi"><div class="wrap"><div class="kicker">Hivatalos népcsoportsajtó</div><h2>Bécsi Magyar Iskola – hírek és cikkek</h2><p class="intro">A Bécsi Magyar Iskoláról szóló cikkek külön gyűjtőoldalon érhetők el a Rólunk.at ausztriai magyar népcsoportsajtó felületén.</p><div class="official-links"><a href="https://rolunk.at/tag/becsi-magyar-iskola/" target="_blank" rel="noopener">Bécsi Magyar Iskola – Rólunk.at hírek ↗</a></div></div></section>\n'''
        if '</main>' in s:
            s=s.replace('</main>',block+'</main>',1)
        else:
            s+=block
p.write_text(s,encoding='utf-8')
