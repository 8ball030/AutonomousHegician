import axios from 'axios';

export default axios.create({
  baseURL: `http://rae.cloud:8080/`
});