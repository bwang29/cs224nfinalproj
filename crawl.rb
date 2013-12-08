require 'nokogiri'  # for parsing html data
require 'mechanize' # for getching html from remote client
require 'json'      # for pasring JSON response from server
require 'rest-client'
require 'open-uri'
require 'uri'

root_url = "http://www.poemhunter.com"
subjects = ["/poems/acrostic/", "/poems/africa/", "/poems/alone/", "/poems/america/", "/poems/angel/", "/poems/anger/", "/poems/animal/", "/poems/anniversary/", "/poems/april/", "/poems/august/", "/poems/autumn/", "/poems/baby/", "/poems/ballad/", "/poems/beach/", "/poems/beautiful/", "/poems/beauty/", "/poems/believe/", "/poems/birth/", "/poems/brother/", "/poems/butterfly/", "/poems/candy/", "/poems/car/", "/poems/carpe%20diem/", "/poems/cat/", "/poems/change/", "/poems/chicago/", "/poems/child/", "/poems/childhood/", "/poems/children/", "/poems/chocolate/", "/poems/christmas/", "/poems/cinderella/", "/poems/city/", "/poems/concrete/", "/poems/couplet/", "/poems/courage/", "/poems/crazy/", "/poems/culture/", "/poems/dance/", "/poems/dark/", "/poems/daughter/", "/poems/death/", "/poems/depression/", "/poems/despair/", "/poems/destiny/", "/poems/discrimination/", "/poems/dog/", "/poems/dream/", "/poems/education/", "/poems/elegy/", "/poems/epic/", "/poems/evil/", "/poems/fairy/", "/poems/faith/", "/poems/family/", "/poems/farewell/", "/poems/fate/", "/poems/father/", "/poems/fear/", "/poems/fire/", "/poems/fish/", "/poems/fishing/", "/poems/flower/", "/poems/fog/", "/poems/food/", "/poems/football/", "/poems/freedom/", "/poems/friend/", "/poems/frog/", "/poems/fun/", "/poems/funeral/", "/poems/funny/", "/poems/future/", "/poems/girl/", "/poems/god/", "/poems/golf/", "/poems/graduate/", "/poems/graduation/", "/poems/greed/", "/poems/green/", "/poems/grief/", "/poems/guitar/", "/poems/haiku/", "/poems/hair/", "/poems/happiness/", "/poems/happy/", "/poems/hate/", "/poems/heart/", "/poems/heaven/", "/poems/hero/", "/poems/history/", "/poems/holocaust/", "/poems/home/", "/poems/homework/", "/poems/honesty/", "/poems/hope/", "/poems/horse/", "/poems/house/", "/poems/howl/", "/poems/humor/", "/poems/hunting/", "/poems/husband/", "/poems/identity/", "/poems/innocence/", "/poems/inspiration/", "/poems/irony/", "/poems/isolation/", "/poems/january/", "/poems/journey/", "/poems/joy/", "/poems/july/", "/poems/june/", "/poems/justice/", "/poems/kiss/", "/poems/laughter/", "/poems/life/", "/poems/light/", "/poems/limerick/", "/poems/london/", "/poems/lonely/", "/poems/loss/", "/poems/lost/", "/poems/love/", "/poems/lust/", "/poems/lyric/", "/poems/magic/", "/poems/marriage/", "/poems/memory/", "/poems/mentor/", "/poems/metaphor/", "/poems/mirror/", "/poems/mom/", "/poems/money/", "/poems/moon/", "/poems/mother/", "/poems/murder/", "/poems/music/", "/poems/narrative/", "/poems/nature/", "/poems/night/", "/poems/ocean/", "/poems/october/", "/poems/ode/", "/poems/pain/", "/poems/paris/", "/poems/passion/", "/poems/peace/", "/poems/people/", "/poems/pink/", "/poems/poem/", "/poems/poetry/", "/poems/poverty/", "/poems/power/", "/poems/prejudice/", "/poems/pride/", "/poems/purple/", "/poems/racism/", "/poems/rain/", "/poems/rainbow/", "/poems/rape/", "/poems/raven/", "/poems/red/", "/poems/remember/", "/poems/respect/", "/poems/retirement/", "/poems/river/", "/poems/romance/", "/poems/romantic/", "/poems/rose/", "/poems/running/", "/poems/sad/", "/poems/school/", "/poems/sea/", "/poems/september/", "/poems/shopping/", "/poems/sick/", "/poems/silence/", "/poems/silver/", "/poems/simile/", "/poems/sister/", "/poems/sky/", "/poems/sleep/", "/poems/smart/", "/poems/smile/", "/poems/snake/", "/poems/snow/", "/poems/soccer/", "/poems/soldier/", "/poems/solitude/", "/poems/sometimes/", "/poems/son/", "/poems/song/", "/poems/sonnet/", "/poems/sorrow/", "/poems/sorry/", "/poems/spring/", "/poems/star/", "/poems/strength/", "/poems/success/", "/poems/suicide/", "/poems/summer/", "/poems/sun/", "/poems/sunset/", "/poems/sunshine/", "/poems/swimming/", "/poems/sympathy/", "/poems/teacher/", "/poems/television/", "/poems/thanks/", "/poems/tiger/", "/poems/time/", "/poems/today/", "/poems/together/", "/poems/travel/", "/poems/tree/", "/poems/trust/", "/poems/truth/", "/poems/valentine/", "/poems/war/", "/poems/warning/", "/poems/water/", "/poems/weather/", "/poems/wedding/", "/poems/wind/", "/poems/winter/", "/poems/woman/", "/poems/women/", "/poems/work/", "/poems/world/"]

def is_number?(num)
    true if Float(num) rescue false
end

puts ARGV[0]
puts ARGV[1]

(ARGV[0].to_i..ARGV[1].to_i).each do |i|
    puts "fetching subjects #{i.to_s} #{subjects[i]}"
    all_poems = File.open("subjects_with_inline_subjects/poem_#{subjects[i].split("/")[2]}.txt", "w")
    (0..40).each do |p|
      raw_html = open(root_url+subjects[i]+"page-#{p}").read
      # puts raw_html
      page = Nokogiri::HTML(raw_html)
      begin
          current_poems = page.css(".poems-about-list li")
          current_poems.each do |li|
              poem_link = li.css("a")[0]['href']
              poem_title = li.css("a")[0].text()
              all_poems.write("[\"#{poem_link}\",\"#{URI.escape(poem_title)}\",\"#{subjects[i]}\"],")
          end
      rescue
          puts "page #{p} in #{i.to_s} ( #{subjects[i]} ) aborted"
      end
      #sleep 0.5
    end
    all_poems.close unless all_poems == nil
end

