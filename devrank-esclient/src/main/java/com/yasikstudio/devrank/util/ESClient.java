package com.yasikstudio.devrank.util;

import java.io.IOException;
import java.io.InputStream;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.util.EntityUtils;

public class ESClient {
  private static final String DATA =
      "{\"script\": \"ctx._source.devrank_score = devrank_score\", \"params\": {\"devrank_score\": %.30f}}";
  private static final String URL = "http://%s/github/users/%s/_update";
  private String hostname;

  public ESClient(String hostname) {
    this.hostname = hostname;
  }

  public synchronized String update(String id, double devrank) {
    String url = String.format(URL, hostname, id);
    String data = String.format(DATA, devrank);
    try {
      return post(url, data);
    } catch (Exception e) {
      throw new RuntimeException("id=" + id + ", devrank=" + devrank + ", url="
          + url);
    }
  }

  private String post(String url, String data) throws ClientProtocolException,
      IOException {
    DefaultHttpClient httpclient = new DefaultHttpClient();
    HttpPost httpPost = new HttpPost(url);
    httpPost.setHeader("Accept", "application/json");
    httpPost.setHeader("Content-Type", "application/json");
    httpPost.setEntity(new StringEntity(data));
    HttpResponse response = httpclient.execute(httpPost);

    String contents = null;
    try {
      HttpEntity entity = response.getEntity();
      contents = getContents(entity.getContent());
      EntityUtils.consume(entity);
    } finally {
      httpPost.releaseConnection();
    }
    return contents;
  }

  private String getContents(InputStream is) {
    StringBuilder sb = new StringBuilder();
    if (is != null) {
      try {
        int len = 0;
        byte[] buf = new byte[1024 * 1024];
        while ((len = is.read(buf)) >= 0) {
          sb.append(new String(buf, 0, len));
        }
      } catch (IOException e) {
        return null;
      } finally {
        try {
          is.close();
        } catch (IOException e) {
          // don't care
        }
      }
    }
    return sb.toString();
  }
}
