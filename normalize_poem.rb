require 'nokogiri'  # for parsing html data
require 'mechanize' # for getching html from remote client
require 'json'      # for pasring JSON response from server
require 'rest-client'
require 'open-uri'
require 'uri'

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


Dir.foreach('poems/') do |item|
  begin
    next if item == '.' or item == '..' or item == ".DS_Store"

    line_num = 0
    file_buf = ""

    # put file lines into arrays
    line_array = []
    text = File.open("poems/#{item}").read
    text.gsub!(/\r\n?/, "\n")
    text.each_line do |line|
      line_array.push line.strip #strip line
    end

    line_array.reject! { |c| c.empty? }
    if line_array.length > 0
      # convert lines
      file_buf += line_array[0] + "\n" # title of the poem
      for i in 1..line_array.length-1
        cur_line = line_array[i]
        prev_line = line_array[i-1]
        if cur_line[0,1].is_upper?
          prev_line_last_char = prev_line[-1,1]
          if prev_line_last_char == "."
            file_buf += " #{cur_line.capitalize}"
          elsif prev_line_last_char == ","
            file_buf += " #{cur_line.uncapitalize}"
          elsif prev_line_last_char == ";"
            file_buf += " #{cur_line.uncapitalize}"
          elsif prev_line_last_char == "\""
            file_buf += " #{cur_line.capitalize}"
          elsif prev_line_last_char == "!"
            file_buf += " #{cur_line.capitalize}"
          elsif prev_line_last_char == "?"
            file_buf += " #{cur_line.capitalize}"
          elsif prev_line_last_char == ":"
            file_buf += " #{cur_line.uncapitalize}"
          elsif prev_line_last_char == "-"
            file_buf += " #{cur_line.uncapitalize}"
          else
            if i > 1 # handle title
              file_buf += ". #{cur_line.capitalize}"
            else
              file_buf += "#{cur_line.capitalize}"
            end
          end
        else
          if i > 1 # handle title
            file_buf += " #{cur_line}"
          else
            file_buf += "#{cur_line.capitalize}"
          end
        end
        # print "#{line_num += 1} #{line} #{line.strip[-1,1]} \n"
      end
      # only write file of poems in certain length
      if file_buf.split(" ").length > 150 && file_buf.split(" ").length < 500

        # reject advertisements and GRE problems "____"
        if file_buf.include?(">") || file_buf.include?("___") || file_buf.include?(".....") || file_buf.include?("http")
          print "A"
          next
        end

        # reject poems that contain really long sentences
        abort_poem_because_poem_is_too_damn_long = false
        sentences = file_buf.split(".")
        for s in 0..sentences.length-1
          if sentences[s].split(" ").length > 150
            abort_poem_because_poem_is_too_damn_long = true
          end
        end
        if abort_poem_because_poem_is_too_damn_long
          print "L"
          next
        end

        print "."
        normalized_word = File.open("poems_normalized/#{item}", "w")
        normalized_word.write(file_buf)
        normalized_word.close unless normalized_word == nil
      end
    end
  rescue
    puts "poem number #{item} aborted"
  end
end

