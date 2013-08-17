package com.yasikstudio.devrank.esclient;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import io.searchbox.client.JestClient;
import io.searchbox.client.JestClientFactory;
import io.searchbox.client.JestResult;
import io.searchbox.client.config.ClientConfig;
import io.searchbox.core.Update;

import java.util.HashMap;
import java.util.Map;

/**
 * Created with IntelliJ IDEA.
 * User: jweb
 * Date: 13. 8. 17.
 * Time: 오후 5:06
 * To change this template use File | Settings | File Templates.
 */
public class ESClient {

  private JestClient client;

  private String indexName;

  public static final String USERS_INDEX_TYPE = "users";

  public static final String USERS_SCORE_UPDATE_SCRIPT
      = "ctx._source.devrank_score = devrank_score";

  public ESClient(String host, String indexName) {
    this.indexName = indexName;
    ClientConfig clientConfig = new ClientConfig.Builder(host).
        multiThreaded(true).build();
    JestClientFactory factory = new JestClientFactory();
    factory.setClientConfig(clientConfig);
    client = factory.getObject();
  }

  public static Map<String, Object> scoreBuildToMap(double score) {
    HashMap<String, Object> map = new HashMap<String, Object>();
    map.put("devrank_score", score);
    return map;
  }

  public boolean update(String type, String id, String _script,
                Map<String, Object> params) {
    try {
      HashMap<String, Object> scriptMap = new HashMap<String, Object>();
      scriptMap.put("script", _script);
      scriptMap.put("params", params);
      Gson gson = new GsonBuilder().disableHtmlEscaping().create();
      String script = gson.toJson(scriptMap, scriptMap.getClass());
      JestResult execute = client.execute(new Update.Builder(script).
          index(indexName).type(type).id(id).build());
      return execute.isSucceeded();
    } catch (Exception e) {
      e.printStackTrace();
      return false;
    }
  }

  public static void main(String[] args) {
    ESClient es = new ESClient("http://jweb.kr:9200", "github");

    // 314555 is jweb
    if (es.update(USERS_INDEX_TYPE, "314555",
        USERS_SCORE_UPDATE_SCRIPT,
        ESClient.scoreBuildToMap(3.5))) {
      System.out.println("DevRank Score update is succeeded.");
    }
    else {
      System.out.println("DevRank Score update is failed.");
    }
  }
}
