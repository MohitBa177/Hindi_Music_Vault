"""
Hindi Music Vault — Catalog Expansion Pass
Expands catalogs to 5,200+ unique tracks across all 8 eras & genres.
"""

import os
import sys
import json
import urllib.request
import urllib.parse

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Referer': 'https://www.jiosaavn.com/',
    'Origin': 'https://www.jiosaavn.com'
}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VAULT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
CATALOGS_DIR = os.path.join(VAULT_ROOT, "Catalogs")

def fetch_saavn(query, count=40):
    try:
        url = 'https://www.jiosaavn.com/api.php?__call=search.getResults&_format=json&_marker=0&api_version=4&ctx=web6dot0&n=' + str(count) + '&p=1&q=' + urllib.parse.quote(query)
        req = urllib.request.Request(url, headers=HTTP_HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        tracks = []
        if data.get('results'):
            for song in data['results']:
                title = song.get('title', '').replace('&quot;', '"').replace('&amp;', '&').strip()
                more_info = song.get('more_info', {})
                singers = more_info.get('singers')
                if not singers:
                    singers = song.get('subtitle', '').split('-')[0].strip()
                if not singers or singers.lower() == 'unknown':
                    singers = 'Various Artists'
                album = more_info.get('album', '').replace('&quot;', '"').replace('&amp;', '&').strip()
                year = song.get('year', '')
                if title:
                    tracks.append({
                        'title': title,
                        'artist': singers,
                        'album': album or 'Bollywood',
                        'year': str(year),
                        'query': f'{title} {singers} {album}'.strip()
                    })
        return tracks
    except Exception:
        return []

def deduplicate(track_list):
    seen = set()
    unique = []
    for t in track_list:
        clean_key = ''.join(e.lower() for e in t.get('title', '') if e.isalnum())
        if clean_key and clean_key not in seen:
            seen.add(clean_key)
            unique.append(t)
    return unique

extra_queries = {
    '01_60s_70s.json': [
        'Naushad Superhits Mughal-e-Azam Baiju Bawra Ganga Jamuna Mother India Kohinoor',
        'Madan Mohan Ghazals Lata Mangeshkar Woh Kaun Thi Mera Saaya Anpadh Jahan Ara',
        'Kalyanji Anandji Qurbani Johny Mera Naam Don Saraswatichandra Safar Sachaa Jhutha',
        'OP Nayyar Asha Rafi Hits Kashmir Ki Kali Ek Musafir Ek Hasina C.I.D. Naya Daur',
        'Salil Chowdhury Madhumati Anand Chhoti Si Baat Rajnigandha Maya Kabuliwala',
        'Jaidev Hum Dono Reshma Aur Shera Gaman',
        'Roshan Taj Mahal Barsaat Ki Raat Mamta Aarti Devar',
        'Khayyam Kabhi Kabhie Trishul Umrao Jaan Noorie Bazaar Razia Sultan',
        'Dev Anand Hits Guide Jewel Thief Tere Ghar Ke Samne Asli Naqli Teen Devian Prem Pujari',
        'Rajesh Khanna Hits Kati Patang Amar Prem Anand Aradhana Safar Dushman Bawarchi Roti Aap Ki Kasam',
        'Shammi Kapoor Dance Rafi Yahoo Teesri Manzil Junglee Brahmachari An Evening in Paris Professor Prince',
        'Dharmendra Hits Phool Aur Patthar Sholay Chupke Chupke Pratiggya Dharam Veer Yaadon Ki Baaraat Seeta Aur Geeta',
        'Amitabh Bachchan 70s Zanjeer Deewaar Sholay Don Muqaddar Ka Sikandar Trishul Kala Patthar Kasme Vaade',
        'Lata Rafi Romantic Duets 60s 70s Hum Dono Leader Ayee Milan Ki Bela Mere Sanam',
        'Kishore Asha Funky Duets RD Burman Jawani Diwani Caravan Apna Desh Yaadon Ki Baaraat',
        'Mukesh Melancholy Sad Hits Anand Mera Naam Joker Kati Patang Pehchan Milan Saraswatichandra',
        'Manna Dey Classical Hits Waqt Zindagi Kaisi Hai Paheli Meri Surat Teri Aankhen Basant Bahar Seema',
        'Hemant Kumar Romantic Melodies Bees Saal Baad Kohraa Baat Ek Raat Ki Khamoshi',
        'Talat Mahmood Ghazals Dil-E-Nadaan Jalte Hain Jiske Liye Sujata Madhumati Footpath',
        'Geeta Dutt Evergreen Baazi Aar Paar Pyaasa Kaagaz Ke Phool C.I.D. Sahib Bibi Aur Ghulam',
        'Mahendra Kapoor Patriotic Upbeat Hits Upkar Kranti Purab Aur Paschim Roti Kapda Aur Makaan Gumrah',
        'Shor 1972 Ek Pyar Ka Nagma Hai Paani Re Paani',
        'Anuraag 1972 Tere Naina Kyon Bhar Aaye Sun Ri Sakhi',
        'Khel Khel Mein 1975 Khullam Khulla Pyar Karenge Ek Main Aur Ek Tu',
        'Kasme Vaade 1978 Kasme Vaade Nibhayenge Hum Aati Rahengi Baharen',
        'Silsila 1981 Yeh Kahan Aa Gaye Hum Dekha Ek Khwab Rang Barse Neela Aasman',
        'Umrao Jaan 1981 In Aankhon Ki Masti Dil Cheez Kya Hai Yeh Kya Jagah Hai Dosto',
        'Ek Duuje Ke Liye 1981 Tere Mere Beech Mein Hum Bane Tum Bane Solah Baras Ki'
    ],
    '02_80s_90s.json': [
        'Nadeem Shravan Hits Aashiqui Saajan Deewana Dil Ka Kya Kasoor Raja Hindustani Pardes Dhadkan Sadak Phool Aur Kaante Jeet Raja Sirf Tum Kasoor Raaz',
        'Jatin Lalit Hits Jo Jeeta Wohi Sikandar DDLJ Yes Boss Ghulam KKHH Sarfarosh Mohabbatein Raju Ban Gaya Gentleman Kabhi Haan Kabhi Naa Khiladi',
        'Anu Malik Blockbusters Baazigar Main Khiladi Tu Anari Akele Hum Akele Tum Judwaa Border Ishq Soldier Josh Refugee Har Dil Jo Pyar Karega Fiza Asoka Ajnabee',
        'Anand Milind Hits QSQT Dil Beta Bol Radha Bol Anari Raja Babu Coolie No 1 Hero No 1 Dulhe Raja Suhaag Gopi Kishan Sanam Bewafa Army',
        'Viju Shah Hits Tridev Vishwatma Mohra Gupt Bade Miyan Chote Miyan Pyaar Ishq Aur Mohabbat Tere Mere Sapne',
        'Govinda Dance Superhits Hero No 1 Coolie No 1 Raja Babu Saajan Chale Sasural Deewana Mastana Aankhen Shola Aur Shabnam Dulhe Raja Haseena Maan Jaayegi',
        'Mithun Chakraborty Disco Hits Disco Dancer Dance Dance Kasam Paida Karne Wale Ki Saaheb Commando Pyar Jhukta Nahin Prem Pratigyaa',
        'Shah Rukh Khan 90s Romantic Hits DDLJ Darr Baazigar Pardes Dil To Pagal Hai KKHH Yes Boss Raju Ban Gaya Gentleman Anjaam Duplicate Baadshah',
        'Salman Khan 90s Hits Maine Pyar Kiya Baaghi Saajan Hum Aapke Hain Koun Karan Arjun Judwaa Pyar Kiya To Darna Kya Hum Dil De Chuke Sanam Biwi No 1 Hum Saath Saath Hain',
        'Aamir Khan 90s Hits QSQT Dil Jo Jeeta Wohi Sikandar Hum Hain Rahi Pyar Ke Rangeela Raja Hindustani Ishq Ghulam Sarfarosh Earth 1947 Mann Dil Chahta Hai',
        'AR Rahman 90s Masterpieces Roja Bombay Rangeela Dil Se Taal 1942 A Love Story Daud Earth 1947',
        'Alka Yagnik Romantic 90s Solos and Duets with Sanu Udit Sonu Abhijeet',
        'Kumar Sanu Top 90s Duets with Alka Anuradha Kavita Sadhana Poornima',
        'Udit Narayan Best 90s Hits DDLJ QSQT Lagaan Mohra Dil Beta Darr Raja Hindustani Kuch Kuch Hota Hai',
        'Kavita Krishnamurthy Classical and Filmi 90s Hits 1942 A Love Story Hum Dil De Chuke Sanam Devdas Khamoshi',
        'Sadhana Sargam 90s Melodies Jo Jeeta Wohi Sikandar Vishwatma Saajan Deewana Mastana Chamatkar',
        'Abhijeet Bhattacharya SRK Hits Yes Boss Baadshah Main Khiladi Tu Anari Darr Josh Khiladiyon Ka Khiladi',
        'Sonu Nigam Early 90s Hits Border Pardes Sangharsh Refugee Taal Dulhan Hum Le Jayenge',
        'SP Balasubrahmanyam Salman Khan Hits Maine Pyar Kiya Hum Aapke Hain Koun Saajan Love 100 Days'
    ],
    '03_2000s.json': [
        'Emraan Hashmi Superhits Murder Zeher Aashiq Banaya Aapne Gangster Aksar Woh Lamhe Awarapan Jannat Raaz 2 Tum Mile OUATIM Crook Murder 2 Jannat 2',
        'Himesh Reshammiya Hits Tere Naam Aashiq Banaya Aapne Aksar Phir Hera Pheri 36 China Town Chup Chup Ke Namastey London Welcome Aap Kaa Surroor Karzzzz Radio',
        'Pritam 2000s Hits Dhoom Gangster Dhoom 2 Metro Jab We Met Bhool Bhulaiyaa Race Jannat Singh Is Kinng Love Aaj Kal APGK Tum Mile All The Best Billu New York',
        'Vishal Shekhar 2000s Hits Jhankaar Beats Musafir Dus Bluffmaster Taxi No 9211 Om Shanti Om Bachna Ae Haseeno Dostana Aladin Tashan I See You Chintuji',
        'Shankar Ehsaan Loy 2000s Hits Dil Chahta Hai Kal Ho Naa Ho Lakshya Bunty Aur Babli KANK Don Taare Zameen Par Rock On Wake Up Sid My Name Is Khan Heyy Babyy',
        'KK Soulful Romantic Hits 2000s Pal Yaaron Tadap Tadap Zara Zara Sach Keh Raha Hai Kya Mujhe Pyar Hai Tu Hi Meri Shab Hai Aankhon Mein Teri Alvida Labon Ko Beete Lamhe Khuda Jaane Dil Ibaadat Haan Tu Hain Tu Jo Mila Mat Aazma Re Zindagi Do Pal Ki Sajde',
        'Sonu Nigam 2000s Masterpieces Kal Ho Naa Ho Suraj Hua Maddham Saathiya Main Hoon Na Do Pal Soniyo Kabhi Alvida Naa Kehna Tanhayee Cham Cham Shukran Allah Guzarish',
        'Shreya Ghoshal 2000s Classics Bairi Piya Silsila Ye Chahat Ka Dola Re Dola Agar Tum Mil Jao Barso Re Teri Ore Pal Pal Har Pal Jaadu Hai Nasha Hai Yeh Ishq Haaye Piya O Re Piya Zoobi Doobi',
        'Sunidhi Chauhan 2000s Dance Hits Ruki Ruki Dhoom Machale Beedi Jalaile Mehboob Mere Aisa Jadoo Desi Girl Chhaliya Crazy Kiya Re Sajna Ve Sajna Dance Pe Chance Chor Bazaari Udi',
        'Atif Aslam 2000s Hits Woh Lamhe Aadat Tere Bin Pehli Nazar Mein Bakhuda Tumhi Ho Tera Hone Laga Hoon Tu Jaane Na Kuch Is Tarah Doorie Mahiya Jal Pari',
        'Mohit Chauhan 2000s Hits Dooba Dooba Tum Se Hi Masakali Genda Phool Yeh Dooriyan Pehli Baar Mohabbat Bheegi Si Bhaagi Si Tune Jo Na Kaha Pee Loon Babaji Ki Booti Kuch Khaas'
    ],
    '04_2010s.json': [
        'Arijit Singh 2010s Complete Hits Tum Hi Ho Channa Mereya Hawayein Ae Dil Hai Mushkil Gerua Samjhawan Muskurane Khamoshiyan Mast Magan Sooraj Dooba Hai Enna Sona Zaalima Phir Bhi Tumko Chahunga Roke Na Ruke Naina Humsafar Lambiyaan Si Judaiyaan Tera Yaar Hoon Main Kalank Pachtaoge Ghungroo Pal Tujhe Kitna Chahne Lage Bekhayali Shayad Ve Maahi Pal Pal Dil Ke Paas Dil Na Jaaneya',
        'Atif Aslam 2010s Blockbusters Jeena Jeena Tu Chahiye Dil Diyan Gallan Dekhte Dekhte O Saathi Tere Sang Yaara Paniyon Sa Main Rang Sharbaton Ka Be Intehaan Piya O Re Piya Dil Kare Darasaniyan Tajdar-e-Haram Baarishein Hoor In Dino',
        'Badshah Bollywood Chartbusters Abhi Toh Party Shuru Hui Hai Kar Gayi Chull Kala Chashma Tareefan Proper Patola Garmi Paani Paani Jugnu Genda Phool Chandigarh Mein Mercy DJ Waley Babu Buzz Voodoo Genda Phool',
        'Yo Yo Honey Singh 2010s Hits Angreji Beat High Heels Dope Shope Blue Eyes Brown Rang Lungi Dance Chaar Botal Vodka Party All Night Sunny Sunny Dheere Dheere Dil Chori Chhote Chhote Peg Makhna Desi Kalakaar Love Dose Birthday Bash One Bottle Down Gal Ban Gayi Gur Nalo Ishq Mitha',
        'Neha Kakkar Superhits Sunny Sunny London Thumakda Manali Trance Mile Ho Tum Aankh Marey Dilbar O Saki Saki Garmi Coca Cola Dil Ko Karaar Aaya Shona Shona Hauli Hauli Yaad Piya Ki Aane Lagi Goa Beach Kanta Laga Taaron Ke Shehar',
        'Amit Trivedi Masterpieces Dev D Iktara Emotional Atyachar Udaan Ishaqzaade Kai Po Che Manja Meethi Boliyan Lootera Monta Re Zinda Queen London Thumakda Highway Patakha Guddi Shaandaar Gulabo Udta Punjab Ikk Kudi Love You Zindagi Dear Zindagi Secret Superstar Main Kaun Hoon Namo Namo Kedarnath Sweetheart Andhadhun Naina Da Kya Kasoor Manmarziyaan Daryaa Grey Walaa Shade',
        'Sachin Jigar Hits Saibo Jeena Jeena Babaji Ki Booti Bezubaan Gulabi Bezubaan Phir Se Dance Basanti Mileya Mileya Sun Saathiya Kamariya Milegi Milegi Apna Bana Le Dance Basanti Shake Your Bootiya Manma Emotion Jaage',
        'Mithoon Soulful Hits Tum Hi Ho Sanam Re Kuch To Hai Humdard Banjaara Phir Bhi Tumko Chahunga Chal Ghar Chalen Kaise Hua Intezaar Dil Sambhal Ja Zara Maula Mere Maula Javeda Zindagi Aye Khuda Madno Bas Ek Pal'
    ],
    '05_2020s_today.json': [
        'Animal 2023 All Songs Satranga Pehle Bhi Main Arjan Vailly Papa Meri Jaan Saari Duniya Jalaa Denge Haiwaan Marham',
        'Stree 2 2024 All Songs Aaj Ki Raat Aayi Nai Khoobsurat Tumhare Hi Rahenge Hum',
        'Pushpa 2 The Rule 2024 Pushpa Pushpa Angaaron The Couple Song Peelings Kissik',
        'Pushpa The Rise 2021 Srivalli Oo Antava Saami Saami Eyy Bidda Idhi Naa Adda',
        'Jawan 2023 All Songs Chaleya Zinda Banda Not Ramaiya Vastavaiya Faraatta Aaradhya',
        'Pathaan 2023 Besharam Rang Jhoome Jo Pathaan Jim Theme',
        'Shershaah 2021 Raataan Lambiyan Ranjha Mann Bharryaa 2 Kabhii Tumhhe Jai Hind Ki Sena',
        'Dunki 2023 Lutt Putt Gaya Nikle The Kabhi Hum Ghar Se O Maahi Banda Waheguru',
        'Bad Newz 2024 Tauba Tauba Jaanam Mere Mehboob Mere Sanam Rabb Warga',
        'Bhool Bhulaiyaa 3 2024 Title Track Ami Je Tomar 3 Beiraada Jaana Samjho Na',
        'Bhool Bhulaiyaa 2 2022 Title Track Ami Je Tomar Mere Dholna De Tali Hum Nashe Mein Toh Nahin',
        'Fighter 2024 Sher Khul Gaye Ishq Jaisa Kuch Heer Aasmani Bekaar Dil Dil Banaane Waaleya',
        'Rocky Aur Rani Kii Prem Kahaani 2023 Tum Kya Mile What Jhumka Ve Kamleya Dhindhora Baje Re Kudmayi Ro Lain De',
        'Brahmastra 2022 Kesariya Deva Deva Rasiya Dance Ka Bhoot',
        'Zara Hatke Zara Bachke 2023 Tere Vaaste Phir Aur Kya Chahiye Baby Tujhe Paap Lagega Sanjha',
        'Tu Jhoothi Main Makkaar 2023 Tere Pyaar Mein Pyaar Hota Kayi Baar Hai O Bedardeya Jaadui Show Me The Thumka Maine Pi Rakhi Hai',
        'Gadar 2 2023 Udd Jaa Kaale Kaava Main Nikla Gaddi Leke Dil Jhoom Khairiyat Chal Tere Ishq Mein',
        'Sam Bahadur 2023 Badhte Chalo Banda Itni Si Baat',
        'Article 370 2024 Dua Main Hoon Bharat',
        'Chandu Champion 2024 Satyanaas Tu Hai Champion Sarphira',
        'Singham Again 2024 Jaane Tu Hey Ram Singham Title',
        'Khel Khel Mein 2024 Hauli Hauli Do U Know Baarlo',
        'Munjya 2024 Taras Haiwan Lori',
        'Amar Singh Chamkila 2024 Naram Kaalja Ishq Mitaye Tu Kya Jaane Baaja Bol Mohabbat Vida Karo',
        'Teri Baaton Mein Aisa Uljha Jiya 2024 Title Track Laal Peeli Akhiyaan Akhiyaan Gulaab Tum Se',
        'Crew 2024 Naina Ghagra Choliya Khwabida',
        'Mr and Mrs Mahi 2024 Dekhha Tenu Rona Sikha De Agar Ho Tum',
        'Laapataa Ladies 2024 Sajni Dheeme Dheeme Beda Paar',
        'Heeriye Jasleen Royal Arijit Singh', 'Soulmate Badshah Arijit Singh', 'Maan Meri Jaan King', 'Tu Hai Kahan AUR'
    ],
    '06_bhajans.json': [
        'Shree Hanuman Chalisa Hariharan Gulshan Kumar T-Series Full Audio',
        'Hanuman Chalisa Shekhar Ravjiani Amit Padhye',
        'Gayatri Mantra Anuradha Paudwal 108 Times',
        'Maha Mrityunjaya Mantra Shankar Sahney 108 Times',
        'Shiv Tandav Stotram Shankar Mahadevan',
        'Namo Namo Kedarnath Amit Trivedi Arijit Singh',
        'Achyutam Keshavam Krishna Bhajan Vikram Hazra Kaun Kehte Hai Bhagwan Aate Nahi',
        'Radhe Radhe Barsane Wali Radhe Gaurav Krishna Goswami',
        'Shri Krishna Govind Hare Murari Hey Nath Narayan Vasudeva Jubin Nautiyal',
        'Aisi Lagi Lagan Meera Ho Gayi Magan Anup Jalota',
        'Payoji Maine Ram Ratan Dhan Payo Lata Mangeshkar',
        'Raghupati Raghav Raja Ram Hariharan',
        'Shri Ram Chandra Kripalu Bhajman Anuradha Paudwal',
        'Bhaye Pragat Kripala Deen Dayala Ram Janam Stuti',
        'Chalo Bulawa Aaya Hai Mata Ne Bulaya Hai Narendra Chanchal Avtar',
        'Tune Mujhe Bulaya Sherawaliye Mohammed Rafi Narendra Chanchal Aasha',
        'Bhor Bhai Din Chhad Gaya Meri Ambe Narendra Chanchal',
        'Ambe Tu Hai Jagdambe Kali Durga Aarti Anuradha Paudwal',
        'Jai Ganesh Deva Ganpati Aarti Anuradha Paudwal',
        'Om Jai Jagdish Hare Vishnu Aarti Anuradha Paudwal',
        'Aarti Kunj Bihari Ki Shri Girdhar Krishna Murari Hariharan',
        'Sukhkarta Dukhharta Ganesh Aarti Lata Mangeshkar',
        'Shendur Lal Chadhayo Ganpati Aarti Vaastav',
        'Sai Ram Sai Shyam Sai Bhagwan Shirdi Ke Data Sabse Mahan Sadhana Sargam',
        'Shirdi Wale Sai Baba Mohammed Rafi Amar Akbar Anthony',
        'Om Namah Shivay Har Har Bhole Namah Shivay Anuradha Paudwal',
        'Karpura Gauram Karunavataram Devotional Chants',
        'Vaishnav Jan To Tene Kahiye Lata Mangeshkar Mahatma Gandhi Bhajan',
        'Mere Ghar Ram Aaye Hain Jubin Nautiyal Payal Dev',
        'Ram Aayenge Toh Angana Sajaaungi Swati Mishra',
        'Kaal Bhairav Ashtakam Agam Shiv Chants',
        'Har Har Shambhu Shiv Mahadeva Abhilipsa Panda Jeetu Sharma',
        'Madhurashtakam Adharam Madhuram Vadanam Madhuram Vikram Hazra',
        'Shri Krishna Sharanam Mamah Dhun Anuradha Paudwal',
        'Jai Laxmi Mata Aarti Anuradha Paudwal Diwali Special',
        'Mata Rani Bhajan Lakhbir Singh Lakkha Pyara Saja Hai Tera Dwar Bhawani',
        'Bhagavad Gita Slokas Chapter 1 to 18 Chanting',
        'Govind Bolo Hari Gopal Bolo Radha Raman Hari Gopal Bolo',
        'Hey Ram Hey Ram Jagjit Singh Bhajan',
        'Itni Shakti Hamein Dena Data Ankush Pushpa Hans Sushma Shrestha'
    ],
    '07_car_highway.json': [
        'Ilahi Yeh Jawaani Hai Deewani Arijit Singh', 'Badtameez Dil Yeh Jawaani Hai Deewani Benny Dayal',
        'Hairat Anjaana Anjaani Lucky Ali Vishal Shekhar', 'Matargashti Tamasha Mohit Chauhan AR Rahman',
        'Sooraj Ki Baahon Mein ZNMD Loy Mendonsa', 'Dil Dhadakne Do Farhan Akhtar Priyanka Chopra',
        'Gallan Goodiyaan Dil Dhadakne Do Shankar Mahadevan', 'Senorita ZNMD Farhan Hrithik Abhay Deol',
        'Patakha Guddi Highway Nooran Sisters AR Rahman', 'Safarnama Tamasha Lucky Ali AR Rahman',
        'Yun Hi Chala Chal Swades Udit Narayan Hariharan AR Rahman', 'Dil Chahta Hai Shankar Mahadevan',
        'Woh Ladki Hai Kahan Dil Chahta Hai Shaan Kavita Krishnamurthy', 'Khaabon Ke Parinday ZNMD Mohit Chauhan Alyssa Mendonsa',
        'Ik Junoon Paint It Red ZNMD Vishal Dadlani', 'Subha Hone Na De Desi Boyz Mika Singh Shefali Alvares',
        'Kar Gayi Chull Kapoor & Sons Badshah Neha Kakkar Fazilpuria', 'London Thumakda Queen Labh Janjua Sonu Kakkar Neha Kakkar',
        'Kala Chashma Baar Baar Dekho Badshah Neha Kakkar Amar Arshi', 'Nashe Si Chadh Gayi Befikre Arijit Singh',
        'Makhna Drive Tanishk Bagchi Yasser Desai Asees Kaur', 'Ghungroo War Arijit Singh Shilpa Rao Vishal Shekhar',
        'Dilliwaali Girlfriend Yeh Jawaani Hai Deewani Arijit Sunidhi', 'Ude Dil Befikre Benny Dayal',
        'Balam Pichkari YJHD Vishal Dadlani Shalmali Kholgade', 'Bulleya Sultan Papon Vishal Shekhar',
        'Bhaag D.K. Bose Delhi Belly Ram Sampath', 'Gallan Kardi Jawaani Jaaneman Jazzy B Jyotica Tangri',
        'Suit Suit Hindi Medium Guru Randhawa Arjun', 'Ban Ja Rani Tumhari Sulu Guru Randhawa',
        'High Rated Gabru Guru Randhawa', 'Lahore Guru Randhawa', 'Bom Diggy Diggy Sonu Ke Titu Ki Sweety Zack Knight Jasmin Walia',
        'Aankh Marey Simmba Neha Kakkar Mika Kumar Sanu', 'Dilbar Satyameva Jayate Neha Kakkar Dhvani Bhanushali',
        'O Saki Saki Batla House Neha Kakkar Tulsi Kumar B Praak', 'Garmi Street Dancer 3D Badshah Neha Kakkar',
        'Muqabla Street Dancer 3D Yash Narvekar Parampara Tandon', 'The Humma Song OK Jaanu Jubin Nautiyal Shashaa Tirupati Badshah',
        'Tauba Tauba Bad Newz Karan Aujla', 'Aaj Ki Raat Stree 2 Madhubanti Bagchi Divya Kumar',
        'Aayi Nai Stree 2 Pawan Singh Simran Choudhary Divya Kumar', 'Chaleya Jawan Arijit Singh Shilpa Rao',
        'Not Ramaiya Vastavaiya Jawan Anirudh Ravichander Vishal Dadlani Shilpa Rao'
    ],
    '08_late_night_chill.json': [
        'Agar Tum Saath Ho Tamasha Arijit Singh Alka Yagnik AR Rahman', 'Kun Faya Kun Rockstar AR Rahman Javed Ali Mohit Chauhan Nizami',
        'Nadaan Parindey Rockstar AR Rahman Mohit Chauhan', 'Phir Le Aya Dil Barfi Arijit Singh Pritam',
        'Iktara Wake Up Sid Kavita Seth Amit Trivedi', 'Kabira Encore YJHD Harshdeep Kaur Arijit Singh Pritam',
        'Shayad Love Aaj Kal Arijit Singh Pritam', 'Baarishein Anuv Jain', 'Alag Aasman Anuv Jain',
        'Husn Anuv Jain', 'Gul Anuv Jain', 'Mishri Anuv Jain', 'Riha Anuv Jain', 'Ocean Anuv Jain',
        'Kasoor Acoustic Prateek Kuhad', 'cold mess Prateek Kuhad', 'Tune Kaha Prateek Kuhad', 'Dil Beparwah Prateek Kuhad',
        'Kho Gaye Hum Kahan Baar Baar Dekho Jasleen Royal Prateek Kuhad', 'Sham Aisha Amit Trivedi Nikhil Dsouza Sunidhi Chauhan',
        'Kaise Hua Kabir Singh Vishal Mishra', 'Bekhayali Acoustic Sachet Tandon', 'Tera Ban Jaunga Kabir Singh Akhil Sachdeva Tulsi Kumar',
        'Tu Aake Dekhle King', 'Maan Meri Jaan King', 'Tu Hai Kahan AUR', 'Tu Jaane Na Unplugged Atif Aslam APGK',
        'Jeena Jeena Unplugged Atif Aslam Badlapur', 'Pehli Nazar Mein Atif Aslam Race', 'Tere Bin Atif Aslam Bas Ek Pal',
        'Dil Mere The Local Train', 'Choo Lo The Local Train', 'Aaoge Tum Kabhi The Local Train', 'Aaftaab The Local Train',
        'Khudi The Local Train', 'Vaaqif The Local Train', 'Mizaaj The Local Train', 'Gulaab The Local Train',
        'Raabta Unplugged Agent Vinod Arijit Singh', 'Samjhawan Unplugged Alia Bhatt Humpty Sharma',
        'Pani Da Rang Ayushmann Khurrana Vicky Donor', 'Saadi Galli Aaja Nautanki Saala Ayushmann Khurrana Neeti Mohan',
        'Nazm Nazm Bareilly Ki Barfi Arko', 'Daryaa Manmarziyaan Ammy Virk Shahid Mallya Amit Trivedi',
        'Tu Kisi Rail Si Masaan Swanand Kirkire Indian Ocean', 'Yeh Fitoor Mera Fitoor Arijit Singh Amit Trivedi',
        'Pashmina Fitoor Amit Trivedi', 'Haminastu Fitoor Zeb Bangash', 'Haareya Meri Pyaari Bindu Arijit Singh Sachin Jigar',
        'Maana Ke Hum Yaar Nahin Parineeti Chopra Sonu Nigam', 'Kinare Queen Mohan Kanan Amit Trivedi',
        'Raanjhanaa Title Track Jaswinder Singh Shiraz Uppal AR Rahman', 'Nazar Laaye Raanjhanaa Rashid Ali Neeti Mohan AR Rahman',
        'Ay Sakhi Raanjhanaa Madhushree Chinmayi AR Rahman', 'Tum Tak Raanjhanaa Javed Ali Pooja Vaidyanath AR Rahman'
    ]
}

total_all = 0
for cat_file, q_list in extra_queries.items():
    cat_path = os.path.join(CATALOGS_DIR, cat_file)
    existing_tracks = []
    if os.path.exists(cat_path):
        with open(cat_path, 'r', encoding='utf-8') as f:
            existing_tracks = json.load(f)
    print(f'[*] Expanding {cat_file} (Current: {len(existing_tracks)} tracks)...')
    new_tracks = []
    for q in q_list:
        res = fetch_saavn(q, count=40)
        new_tracks.extend(res)
    combined = deduplicate(existing_tracks + new_tracks)
    for idx, t in enumerate(combined, start=1):
        t['track_num'] = idx
    with open(cat_path, 'w', encoding='utf-8') as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
    print(f'    [+] Updated {cat_file} -> {len(combined)} tracks')
    total_all += len(combined)

print('=' * 70)
print(f'TOTAL UNIQUE TRACKS IN MASTER ARCHIVE: {total_all}')
print('=' * 70)
