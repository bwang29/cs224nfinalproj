require 'nokogiri'  # for parsing html data
require 'mechanize' # for getching html from remote client
require 'json'      # for pasring JSON response from server
require 'rest-client'
require 'open-uri'
require 'uri'

root_url = "https://medium.com/"
subjects = ["/about", "/adventures-in-consumer-technology", "/african-makers", "/american-dreamers", "/architecting-a-life", "/armchair-economics", "/best-thing-i-found-online-today", "/better-humans", "/boinkology-101", "/book-excerpts", "/career-pathing", "/changing-city", "/click-the-shutter", "/comedy-corner", "/race-class", "/customer-dissatisfaction", "/dear-blank", "/design-startups", "/design-ux", "/editors-picks", "/epic-magazine", "/evidence-base", "/failure-inc", "/the-ingredients-2", "/freelancers-life", "/futures-exchange", "/geek-empire", "/gender-justice-feminism", "/how-to-use-the-internet", "/human-parts", "/i-3-video-games", "/i-m-h-o", "/ladybits-on-medium", "/law-of-the-land", "/lessons-learned", "/life-hacks", "/look-what-i-made", "/looking-up", "/matt-bors", "/matter", "/help-center", "/medium-ideas", "/medium-writers-guide", "/medium-long", "/mobile-culture", "/my-modern-marriage", "/nanowrimo-2013-1", "/new-media", "/non-english-collections-on-medium", "/off-the-script", "/on-coding", "/on-management", "/on-publishing", "/on-startups", "/open-source-family", "/de-cultura", "/people-gadgets", "/play-time", "/pop-of-culture", "/product-design", "/roaming-the-earth", "/sports-page", "/surveillance-state", "/surviving-the-future", "/teaching-learning", "/tech-talk", "/the-nib", "/obvious", "/the-physics-arxiv-blog", "/the-t-v-age", "/the-year-of-the-looking-glass", "/this-could-be-better", "/this-happened-to-me", "/thoughts-on-creativity", "/turkeys-pilgrims", "/unforgettable-moments", "/war-is-boring", "/we-live-in-the-future", "/weird-future", "/what-i-learned-building", "/what-i-learned-today", "/what-im-thankful-for", "/who-i-am", "/who-needs-art", "/jobs", "/world-of-music", "/writers-on-writing"]

puts ARGV[0]
puts ARGV[1]
all_feed = File.open("medium_feed_nov_2013.txt", "w")

(0..subjects.length-1).each do |i|
    puts "fetching subjects #{i.to_s} #{subjects[i]}"
    raw_feed = open(root_url+"feed"+subjects[i]).read
    #puts raw_feed
    page = Nokogiri::XML(raw_feed)
    begin
        current_posts = page.css("link")
        current_posts.each do |po|
            if po.text().split("/").length > 4
              all_feed.write("[\"#{po.text()}\",\"#{subjects[i]}\"],\n")
            end
        end
    rescue
        puts "page #{p} in #{i.to_s} ( #{subjects[i]} ) aborted"
    end

end
all_feed.close unless all_feed == nil
