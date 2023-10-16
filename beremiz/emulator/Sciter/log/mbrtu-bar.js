const BLACK = "#000000"
const RED = "#FF0000"
const YELLOW = "#FFFF00"
const WHITE = "#FFFFFF"

export class MbrtuLog extends Element{
  messages = []
  write(message)
  {
    for (let msg of message)
    {
      this.messages.push(msg);
    }
    this.prependElements(this.messages.length-message.length, message.length)
    
    return true;
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
    let time = this.messages[index].time

    let dir = this.messages[index].direction
    
    let msg = this.messages[index].mbrtu_msg

    let service_msg = this.messages[index].service_msg
    
    //return <div key={index}>{`${time}:  ${dir}  ${msg}`}</div>;
    return <tr key={index}>
              <td>{time}</td>
              <td>{dir}</td>
              <td>{msg}</td>
              <td>{service_msg}</td>
          </tr>;
    //return <div key={index}>{message}</div>;
  }
  /*TODO Test mbrtu пульт.
  renderList(items) // overridable
  {
      return <virtual-select {this.messages} styleset={this.styleset}>{ items }</virtual-select>; 
  }*/

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

