// Piste AI EVANGELISTS - GA4 SEO分析レポート取得スクリプト
// 測定ID: G-LR35246V7B
//
// 使い方:
// 1. findPropertyId() を実行 → ログにプロパティIDが出力される
// 2. 下のPROPERTY_IDにその数値を入力
// 3. main() を実行 → 4シートにGA4データが出力される

const PROPERTY_ID = '531067300'; // GA4プロパティID（数値）

// プロパティIDを検索する関数（初回のみ実行）
// GA4管理画面のURL https://analytics.google.com/analytics/web/#/p{PROPERTY_ID}/... から確認もできます
function findPropertyId() {
  // Analytics Admin API でアカウント一覧を取得
  const token = ScriptApp.getOAuthToken();

  // 方法1: Account Summariesを取得
  const url1 = 'https://analyticsadmin.googleapis.com/v1beta/accountSummaries';
  const res1 = UrlFetchApp.fetch(url1, {
    headers: { 'Authorization': 'Bearer ' + token },
    muteHttpExceptions: true
  });
  Logger.log('=== Account Summaries ===');
  Logger.log(res1.getContentText());

  // 方法2: アカウント一覧を取得
  const url2 = 'https://analyticsadmin.googleapis.com/v1beta/accounts';
  const res2 = UrlFetchApp.fetch(url2, {
    headers: { 'Authorization': 'Bearer ' + token },
    muteHttpExceptions: true
  });
  Logger.log('=== Accounts ===');
  Logger.log(res2.getContentText());

  // 方法3: 測定IDからプロパティを検索（G-LR35246V7B）
  // searchDataStreamsで測定IDからプロパティIDを逆引き
  const data1 = JSON.parse(res1.getContentText());
  if (data1.accountSummaries) {
    for (const account of data1.accountSummaries) {
      Logger.log('Account: ' + account.displayName + ' (' + account.account + ')');
      if (account.propertySummaries) {
        for (const prop of account.propertySummaries) {
          Logger.log('  Property: ' + prop.displayName + ' → ' + prop.property);
        }
      }
    }
  }
}

function main() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const propertyId = PROPERTY_ID;

  // 各レポートを取得
  getOverviewReport(ss, propertyId);
  getTrafficReport(ss, propertyId);
  getPageReport(ss, propertyId);
  getUserAttributeReport(ss, propertyId);

  SpreadsheetApp.getUi().alert('GA4データの取得が完了しました！');
}

// === 基本指標（過去28日間） ===
function getOverviewReport(ss, propertyId) {
  const sheet = getOrCreateSheet(ss, '概要');
  sheet.clear();

  const request = AnalyticsData.newRunReportRequest();
  request.dateRanges = [AnalyticsData.newDateRange()];
  request.dateRanges[0].startDate = '28daysAgo';
  request.dateRanges[0].endDate = 'today';

  request.metrics = [
    newMetric('activeUsers'),
    newMetric('newUsers'),
    newMetric('sessions'),
    newMetric('engagementRate'),
    newMetric('averageSessionDuration'),
    newMetric('screenPageViews'),
    newMetric('bounceRate')
  ];

  const response = AnalyticsData.Properties.runReport(request, 'properties/' + propertyId);

  sheet.appendRow(['GA4 基本指標（過去28日間）', '', new Date()]);
  sheet.appendRow(['']);
  sheet.appendRow(['指標', '値']);

  const metricNames = ['アクティブユーザー', '新規ユーザー', 'セッション数', 'エンゲージメント率', '平均セッション時間(秒)', 'ページビュー', '直帰率'];

  if (response.rows && response.rows.length > 0) {
    const row = response.rows[0];
    for (let i = 0; i < row.metricValues.length; i++) {
      let val = row.metricValues[i].value;
      if (metricNames[i].includes('率')) {
        val = (parseFloat(val) * 100).toFixed(1) + '%';
      } else if (metricNames[i].includes('時間')) {
        val = parseFloat(val).toFixed(0) + '秒';
      }
      sheet.appendRow([metricNames[i], val]);
    }
  }

  sheet.autoResizeColumns(1, 2);
}

// === トラフィック獲得（チャネル別） ===
function getTrafficReport(ss, propertyId) {
  const sheet = getOrCreateSheet(ss, 'トラフィック獲得');
  sheet.clear();

  const request = AnalyticsData.newRunReportRequest();
  request.dateRanges = [AnalyticsData.newDateRange()];
  request.dateRanges[0].startDate = '28daysAgo';
  request.dateRanges[0].endDate = 'today';

  request.dimensions = [newDimension('sessionDefaultChannelGroup')];
  request.metrics = [
    newMetric('sessions'),
    newMetric('activeUsers'),
    newMetric('engagementRate'),
    newMetric('averageSessionDuration'),
    newMetric('conversions')
  ];
  request.orderBys = [AnalyticsData.newOrderBy()];
  request.orderBys[0].metric = AnalyticsData.newMetricOrderBy();
  request.orderBys[0].metric.metricName = 'sessions';
  request.orderBys[0].desc = true;

  const response = AnalyticsData.Properties.runReport(request, 'properties/' + propertyId);

  sheet.appendRow(['トラフィック獲得（過去28日間）', '', '', '', '', new Date()]);
  sheet.appendRow(['']);
  sheet.appendRow(['チャネル', 'セッション数', 'アクティブユーザー', 'エンゲージメント率', '平均セッション時間', 'コンバージョン']);

  if (response.rows) {
    for (const row of response.rows) {
      sheet.appendRow([
        row.dimensionValues[0].value,
        row.metricValues[0].value,
        row.metricValues[1].value,
        (parseFloat(row.metricValues[2].value) * 100).toFixed(1) + '%',
        parseFloat(row.metricValues[3].value).toFixed(0) + '秒',
        row.metricValues[4].value
      ]);
    }
  }

  sheet.autoResizeColumns(1, 6);
}

// === ページ別アクセス（上位20ページ） ===
function getPageReport(ss, propertyId) {
  const sheet = getOrCreateSheet(ss, 'ページ別');
  sheet.clear();

  const request = AnalyticsData.newRunReportRequest();
  request.dateRanges = [AnalyticsData.newDateRange()];
  request.dateRanges[0].startDate = '28daysAgo';
  request.dateRanges[0].endDate = 'today';

  request.dimensions = [newDimension('pagePath'), newDimension('pageTitle')];
  request.metrics = [
    newMetric('screenPageViews'),
    newMetric('activeUsers'),
    newMetric('averageSessionDuration'),
    newMetric('engagementRate')
  ];
  request.orderBys = [AnalyticsData.newOrderBy()];
  request.orderBys[0].metric = AnalyticsData.newMetricOrderBy();
  request.orderBys[0].metric.metricName = 'screenPageViews';
  request.orderBys[0].desc = true;
  request.limit = 20;

  const response = AnalyticsData.Properties.runReport(request, 'properties/' + propertyId);

  sheet.appendRow(['ページ別アクセス TOP20（過去28日間）', '', '', '', '', new Date()]);
  sheet.appendRow(['']);
  sheet.appendRow(['パス', 'ページタイトル', '表示回数', 'ユーザー数', '平均滞在時間', 'エンゲージメント率']);

  if (response.rows) {
    for (const row of response.rows) {
      sheet.appendRow([
        row.dimensionValues[0].value,
        row.dimensionValues[1].value,
        row.metricValues[0].value,
        row.metricValues[1].value,
        parseFloat(row.metricValues[2].value).toFixed(0) + '秒',
        (parseFloat(row.metricValues[3].value) * 100).toFixed(1) + '%'
      ]);
    }
  }

  sheet.autoResizeColumns(1, 6);
}

// === ユーザー属性 ===
function getUserAttributeReport(ss, propertyId) {
  const sheet = getOrCreateSheet(ss, 'ユーザー属性');
  sheet.clear();

  let currentRow = 1;

  // デバイス別
  sheet.getRange(currentRow, 1).setValue('デバイス別（過去28日間）');
  currentRow += 2;
  sheet.getRange(currentRow, 1, 1, 3).setValues([['デバイス', 'ユーザー数', 'セッション数']]);
  currentRow++;

  const deviceReq = AnalyticsData.newRunReportRequest();
  deviceReq.dateRanges = [AnalyticsData.newDateRange()];
  deviceReq.dateRanges[0].startDate = '28daysAgo';
  deviceReq.dateRanges[0].endDate = 'today';
  deviceReq.dimensions = [newDimension('deviceCategory')];
  deviceReq.metrics = [newMetric('activeUsers'), newMetric('sessions')];
  deviceReq.orderBys = [AnalyticsData.newOrderBy()];
  deviceReq.orderBys[0].metric = AnalyticsData.newMetricOrderBy();
  deviceReq.orderBys[0].metric.metricName = 'activeUsers';
  deviceReq.orderBys[0].desc = true;

  const deviceRes = AnalyticsData.Properties.runReport(deviceReq, 'properties/' + propertyId);
  if (deviceRes.rows) {
    for (const row of deviceRes.rows) {
      sheet.getRange(currentRow, 1, 1, 3).setValues([[
        row.dimensionValues[0].value,
        row.metricValues[0].value,
        row.metricValues[1].value
      ]]);
      currentRow++;
    }
  }

  currentRow += 2;

  // 地域別
  sheet.getRange(currentRow, 1).setValue('地域別 TOP10（過去28日間）');
  currentRow += 2;
  sheet.getRange(currentRow, 1, 1, 3).setValues([['都市', 'ユーザー数', 'セッション数']]);
  currentRow++;

  const cityReq = AnalyticsData.newRunReportRequest();
  cityReq.dateRanges = [AnalyticsData.newDateRange()];
  cityReq.dateRanges[0].startDate = '28daysAgo';
  cityReq.dateRanges[0].endDate = 'today';
  cityReq.dimensions = [newDimension('city')];
  cityReq.metrics = [newMetric('activeUsers'), newMetric('sessions')];
  cityReq.orderBys = [AnalyticsData.newOrderBy()];
  cityReq.orderBys[0].metric = AnalyticsData.newMetricOrderBy();
  cityReq.orderBys[0].metric.metricName = 'activeUsers';
  cityReq.orderBys[0].desc = true;
  cityReq.limit = 10;

  const cityRes = AnalyticsData.Properties.runReport(cityReq, 'properties/' + propertyId);
  if (cityRes.rows) {
    for (const row of cityRes.rows) {
      sheet.getRange(currentRow, 1, 1, 3).setValues([[
        row.dimensionValues[0].value,
        row.metricValues[0].value,
        row.metricValues[1].value
      ]]);
      currentRow++;
    }
  }

  sheet.autoResizeColumns(1, 3);
}

// === ヘルパー関数 ===
function newMetric(name) {
  const m = AnalyticsData.newMetric();
  m.name = name;
  return m;
}

function newDimension(name) {
  const d = AnalyticsData.newDimension();
  d.name = name;
  return d;
}

function getOrCreateSheet(ss, name) {
  let sheet = ss.getSheetByName(name);
  if (!sheet) {
    sheet = ss.insertSheet(name);
  }
  return sheet;
}
