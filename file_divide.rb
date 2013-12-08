require 'nokogiri'  # for parsing html data
require 'mechanize' # for getching html from remote client
require 'json'      # for pasring JSON response from server
require 'rest-client'
require 'open-uri'
require 'uri'

$target_folder = "medium_posts"

class String
  def is_upper?
    self == self.upcase
  end
  def is_lower?
    self == self.downcase
  end
  def uncapitalize
    self[0, 1].downcase + self[1..-1]
  end
  def capitalize
    self[0, 1].upcase + self[1..-1]
  end
end

def write_divided_file(filename_original, part, title, msg)
  fw = File.open("#{$target_folder}_divided/#{filename_original.split('txt')[0]}#{part}.txt", "w")
  fw.write(title+"\n")
  fw.write(msg+". ")
  fw.close unless fw == nil
end

def divide_file(sentences,file_name,title)
  if sentences.length <= 10
    return
  end
  num_parts = sentences.length/10
  divide_idx = sentences.length/num_parts
  for i in 0...num_parts
    divided_text = sentences[(i*divide_idx)..((i+1)*divide_idx-1)].join(". ")
    write_divided_file(file_name, "pp#{i}", title, divided_text)
  end
end

Dir.foreach("#{$target_folder}/") do |item|
  item_hash = {}
  begin
    next if item == '.' or item == '..' or item == ".DS_Store"

    h = item.split("_").last
    if !item_hash.has_key?(h)
      item_hash[h] = true
    else
      next
    end

    line_num = 0
    file_buf = ""

    # put file lines into arrays
    line_array = []
    text = File.open("#{$target_folder}/#{item}").read
    text.gsub!(/\r\n?/, "\n")
    text.each_line do |line|
      line_array.push line.strip #strip line
    end

    line_array.reject! { |c| c.empty? }

    sentences = line_array[1].split(".")
    if sentences.length > 30
      puts "dividing #{item}"
      # time to divide
      divide_file(sentences,item,line_array[0])
    end
  rescue
    puts "file #{item} aborted"
  end
end

