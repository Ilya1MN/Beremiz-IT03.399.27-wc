const BLACK = "#000000"
const RED = "#FF0000"
const YELLOW = "#FFFF00"
const WHITE = "#FFFFFF"

//let messages = []

export function InitEventLog(){
  let debug_log;
  debug_log = document.$("debug_log")
  document.addEventListener("write", (evt)=>{ return debug_log.write(evt.data.msg); })
  document.addEventListener("write_error", (evt)=>{ return debug_log.write_error(evt.data.msg); })
  document.addEventListener("write_warning", (evt)=>{ return debug_log.write_warning(evt.data.msg); })
}

export class DebugLog extends Element{
  messages = []
  clear(){
    this.messages = [];
    this.componentUpdate();
  }

  write(message, text_color=BLACK, background_color=WHITE)
  {
    let time = new Date()
    let time_string = `${time.toTimeString().split(" ")[0]}:  `

    let message_data = {message: time_string + message, text_color: text_color, background_color: background_color}
    this.messages.push(message_data);
    this.appendElements(this.messages.length-1, 1)
    return true;
  }

  write_error(message)
  {
    return this.write("ERROR: " + message, RED, YELLOW)
  }

  write_warning(message)
  {
    return this.write("WARNING: " + message, RED, WHITE)
  }
      // scroll down
    appendElements(index, n) {
      if (index === undefined) index = 0;
      const elements = [];
      for (let i = 0; i < n; ++i, ++index) {
        if (index >= this.messages.length) break;
        elements.push(this.renderItem(index));
      }

      this.append(elements);
      return {moreafter: (this.messages.length - index)}; // return estimated number of items below this chunk
    }

// scroll up
  prependElements(index, n) {
    if (index === undefined) index = this.messages.length - 1;
    const elements = [];
    for (let i = 0; i < n; ++i, --index) {
      if (index < 0) break;
      elements.push(this.renderItem(index));
    }

    elements.reverse();
    this.prepend(elements);
    return {morebefore: (index < 0 ? 0 : index + 1)}; // return estimated number of items above this chunk
  }

// scroll to
  replaceElements(index, n) {
    const elements = [];
    const start = index;
    for (let i = 0; i < n; ++i, ++index) {
      if (index >= this.messages.length) break;
      elements.push(this.renderItem(index));
    }

    this.patch(elements);
    return {
      morebefore: (start <= 0 ? 0 : start),
      moreafter: (this.messages.length - index),
    }; // return estimated number of items before and above this chunk
  }

  renderItem(index) {
    let message = this.messages[index].message
    let color_b = this.messages[index].background_color
    let color_t = this.messages[index].text_color
    
    return <div key={index} style={`color: ${color_t}; background-color: ${color_b};`}>{message}</div>;
    //return <div key={index}>{message}</div>;
  }

  oncontentrequired(evt) {
    const {length, start, where} = evt.data;

    if (where > 0)
    // scrolling down, need to append more elements
      evt.data = this.appendElements(start, length);
    else if (where < 0)
    // scrolling up, need to prepend more elements
      evt.data = this.prependElements(start, length);
    else
    // scrolling to index
      evt.data = this.replaceElements(start, length);

    return true;
  }
}

