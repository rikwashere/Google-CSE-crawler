<h2>Google CSE crawler<h2>
<p>A script that uses Google CSE (Custom Search Engines) to automatically search selected sites for certain keywords. This script was used to find sites of Dutch media that used tweets of Russian trolls in their articles.</p> 

<a href='https://www.nrc.nl/nieuws/2017/12/08/media-nederland-citeerden-trollen-als-bron-a1584306'>Read the full article here [Dutch]</a>

<p>The CSEs are fed keywords from a list of troll Twitter handles, which have been identified by Twitter and publicized by the American Senate. Selenium is used to operate the search engine and to avoid (unsuccesfully) rate limits. Instead multiple, but equal CSEs are used: the script cycles them (it works o-kay). HTML is scraped using BeautifulSoup.</p>

<p>Application context:</p>
<ul>
  <li>Ubuntu 16.04 LTS (64-bit)</li>
  <li>Firefox 60.0.2</li>
  <li>Python 2.7.12</li>
  <li>Selenium 3.12.0</li>
  <li>Geckodriver v0.21.0 (<a href='https://github.com/mozilla/geckodriver/releases'>get here</a>)</li>
</ul>

<p>Results are written to a JSON-file, which is also used to keep track of where the script left off, in case of breakages (which occur often). </p>
