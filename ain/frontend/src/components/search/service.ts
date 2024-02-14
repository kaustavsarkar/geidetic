import { FileItemList } from "./model";

const isLocal = import.meta.env.MODE === "development";

export default class SearchService {
  _searchResult =
    JSON.parse(`{"searchItems":[{"filePath":"/home/kaustav/work/ain/legal_gk.pdf","pages":["253","254","250","252","255","251","249","22","78","237","126","215","94","92","60","113","125","110","111","240","130","5","105","151","203","121","107","2","216","218","99","116","222","145","136","115","153","220","80","164","81","102","98","64","195","213","79","118","119","114","221","0","85","120","35","238","217","243","135","207","117","112","63","143","224","95","223","91","132","127","27","6","11","206","146","90","219","209","131","202","227","239","236","86","230","8","88","69","84","106","155","134","139","198","212","199","138","129","194","200","193","232","211","154","149","93","89","82","100","104","62","47","225","247","101","83","177","256","133","9","3","167","59","168","21","242","205","108","159","42","55","124","16","214","128","226","228","17","65","144","234","14","192","15","231","66","150","173","170","109","96","87","67","68","137","97","10","61"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1251.pdf","pages":["137","112","18","88","110","117","111","17","47","140","48","69","125","16","9","51","45","89","142","71","145","4","15","118","73","52","87","119","46","113","148","105","90","38","104","19","84","70","150","146","102","139","37","126","123","59","85","136","3","56","141","127","128","68","74","149","144","72","138","134","116","1","75","33","115","101","94","92","2","57","14","147","151","39","32","100","54","22","95","78","21","96","8","143","97","31","23","99","41","24","20","114","83","124","63","49","103","93","13","122","62","130","91","86","64","106","108","76","66","25","67","5","152","36","27","10","35","29","109","79","7","6","60","61","44","34","28","12","11","120","65","53","50","40","107","77","132","98","131"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1250.pdf","pages":["3","4","2","0"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1259.pdf","pages":["6","0","4","3","5","7","1"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1227.pdf","pages":["36","42","37","40","15","4","38","39","20","21","7","32","35","28","14","6","43","44","41","27","26","22","25","5","30","2","1","19","9","8","13","23","10","34","16","24","12","3"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1248.pdf","pages":["8","3","7","4","6","2","5","0","9","10"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1224.pdf","pages":["19","45","28","41","20","27","44","22","37","34","16","13","33","17","1","25","46","0","2","3","24","6","18","36","23","14","10","43","26","7","42","35"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1244.pdf","pages":["6","9","3","8","0","1","4","2","7"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1249.pdf","pages":["30","31","12","3","36","11","14","28","35","9","33","10","21","22","24","23","7","1","15","2","29","27","19","34","18","25"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1245.pdf","pages":["8","6","1","7","5","4","0","3"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1252.pdf","pages":["3","11","10","2","9","8","0","7"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1242.pdf","pages":["38","23","46","39","19","15","45","31","28","29","35","30","11","32","24","2","12","59","18","37","6","5","48","14","8","63","9","43","44"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1234.pdf","pages":["4","1","5","7","0","6"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1235.pdf","pages":["2","1","0","4","3"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1221.pdf","pages":["16","9","8","15","14","6","12","7","1","11","13"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1263.pdf","pages":["5","3","2","6"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1225.pdf","pages":["3"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1240.pdf","pages":["2","4","1","0","3"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1222.pdf","pages":["3","2"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1253.pdf","pages":["11","12","10","3","4","6"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1220.pdf","pages":["0","4","5"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1223.pdf","pages":["1","2"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1255.pdf","pages":["3"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1262.pdf","pages":["3","6","4","5"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1243.pdf","pages":["2","5","3"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1231.pdf","pages":["2","3"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1254.pdf","pages":["2","0"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1258.pdf","pages":["3","5","6"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1228.pdf","pages":["6","8","1","4"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1238.pdf","pages":["5","1","4","6"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1233.pdf","pages":["7","6","1","2"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1260.pdf","pages":["17","15","13"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1257.pdf","pages":["31","30","21","22","15","33","8","32"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1232.pdf","pages":["4"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1236.pdf","pages":["0","3"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1256.pdf","pages":["26","20","11","13","21","7","9"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1229.pdf","pages":["4"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1247.pdf","pages":["1","5","2"]},{"filePath":"/home/kaustav/work/ain/sc-scraper/output/01-01-1950/_1237.pdf","pages":["3"]}]}
`);

  search = async (searchText: string): Promise<FileItemList | null> => {
    if (isLocal) {
      return new FileItemList(this._searchResult);
    }
    try {
      const response = await fetch(`http://localhost:5000/search`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ searchString: searchText }),
      });

      if (response.ok) {
        return new FileItemList(await response.json());
      }
    } catch (e) {
      console.log(e);
    }
    return null;
  };

  open = async (filePath: string, pageNumber: string): Promise<void> => {
    if (isLocal) {
      return;
    }
    try {
      const response = await fetch(`http://localhost:5000/openpdf`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ filePath: filePath, pageNumber: pageNumber }),
      });

      if (response.ok) {
        return;
      }
    } catch (e) {
      console.log(e);
    }
    return;
  };
}
