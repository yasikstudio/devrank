package com.yasikstudio.devrank.merge;

import java.util.List;

import com.yasikstudio.devrank.model.User;
import com.yasikstudio.devrank.model.Weight;

public class MergeUtils {

  public static void merge(User dest, User src) {
    merge(dest.getFollowings(), src.getFollowings());
    merge(dest.getForks(), src.getForks());
    merge(dest.getPulls(), src.getPulls());
    merge(dest.getStars(), src.getStars());
    merge(dest.getWatchs(), src.getWatchs());
  }

  public static void merge(List<Weight> dest, List<Weight> src) {
    for (Weight w : src) {
      merge(dest, w);
    }
  }

  public static void merge(List<Weight> dest, Weight src) {
    String id = src.getId();
    int count = src.getCount();

    for (Weight w : dest) {
      // if, src exists in dest, add count
      if (id.equals(w.getId())) {
        w.setCount(w.getCount() + count);
        return;
      }
    }

    // when, src not exists in dest. append this.
    dest.add(src);
  }

}
