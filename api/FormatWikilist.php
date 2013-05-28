<?php	
	/*
	 * Outputs the query as a wikilist
	 * TO DO:
	 *   bettwer way of outputting all objects of a given query (i.e. continue/offset param)
	 *   stick variables in head (and hide from row) based on query
	 *      e.g. if query involves municipalityName=Malmö then: {{../huvud|kommun=Malmö}} and {{../rad|gömKommun=|...}} remove kommun from output
	 */
	class FormatWikilist{
		private function writeHeader(){
			/* Closing table and adding cateogires? */
			$text = "{{Användare:André Costa (WMSE)/Skulpturlistor/huvud}}\n";
			# potential of adding parameters (based on search parameters)
			return $text;
		}
		
		private function writeEnder(){
			/* Closing tavle and adding cateogires? */
			$text = "|}\n";
			return $text;
		}
		
		private function writeRow($row, $muni_names, $county_names){
			#mod get fromWikidata... to either return url or just article name
			#format indoors ("inside")
			#material
			$row = $row['hit'];
			$text ="{{Användare:André Costa (WMSE)/Skulpturlistor/rad";
			$text .="\n| id           = ";
			if (!empty($row['id']))
				$text .=$placemarkId = $row['source'].'/'.$row['id'];
			$text .="\n| id-länk      = ";
			if (!empty($row['official_url']))
				$text .=$row['official_url'];
			$text .="\n| titel        = ";
			if (!empty($row['title']))
				$text .=$row['title'];
			$text .="\n| artikel      = ";
			if (!empty($row['wiki_article']))
				$text .= ApiBase::getArticleFromWikidata($row['wiki_article'], $getUrl=false);
			$text .="\n| konstnär     = ";
			$artistName = self::outputArtist($row);
			if (!empty($artistName))
				$text .=$artistName;
			$text .="\n| årtal        = ";
			if (!empty($row['year']))
				$text .=$row['year'];
			$text .="\n| beskrivning  = ";
			if (!empty($row['descr']))
				$text .=$row['descr'];
			$text .="\n| typ          = ";
			if (!empty($row['type']))
				$text .=$row['type'];
			$text .="\n| material     = ";
			if (!empty($row['material']))
				$text .=$row['material'];
			$text .="\n| fri          = ";
			if (!empty($row['free'])){
				if ($row['free'] == 'unfree')
					$text .="nej";
				else
					$text .=$row['free'];
			}
			$text .="\n| plats        = ";
			if (!empty($row['address']))
				$text .=$row['address'];
			$text .="\n| inomhus      = ";
			if (!empty($row['inside'])){
				if(ord($row['inside'])==1)
					$text .= "ja";
			}
			$text .="\n| län          = ";
			if (!empty($row['county']))
				$text .=$county_names[$row['county']];
			$text .="\n| kommun       = ";
			if (!empty($row['muni']))
				$text .=$muni_names[$row['muni']];
			$text .="\n| stadsdel     = ";
			if (!empty($row['district']))
				$text .=$row['district'];
			$text .="\n| lat          = ";
			if (!empty($row['lat']))
				$text .=$row['lat'];
			$text .="\n| lon          = ";
			if (!empty($row['lon']))
				$text .=$row['lon'];
			$text .="\n| bild         = ";
			if (!empty($row['image']))
				$text .=$row['image'];
			$text .="\n| commonscat   = ";
			if (!empty($row['commons_cat']))
				$text .=$row['commons_cat'];
			$text .="\n}}\n";
			return $text;
		}
		
		function outputArtist($row){
			$artist_info = ApiBase::getArtistInfo($row['id']);
			if (!empty($artist_info)){
				$desc ='';
				$counter=2;
				foreach ($artist_info as $ai){
					if($ai['wiki']){
						$desc .= "[[".ApiBase::getArticleFromWikidata($ai['wiki'], $getUrl=false);
						$desc .= "|".$ai['name'];
						$desc .= "]]";
					} else
						$desc .= $ai['name'];
					if (count($artist_info) >= $counter){
						$desc .= "\n| konstnär".$counter."    = ";
						$counter++;
					}
				}
				return $desc; 
			}
			elseif (!empty($row['artist']))
				return $row['artist'];
		}
		
		function outputWarning($head){
			if (!empty($head['continue']))
				$text = $head['hits'];
			if (!empty($head['warning']))
				$text .="\nWarning: ".$head['warning'];
			if (!empty($text))
				$text = "<!--".$text."-->\n";
			return $text;
		}
		
		function output($results){
			if($results['head']['status'] == '0') #Fall back to xml if errors
				Format::outputXml($results);
			else{
				@header ("content-type: text/plain;charset=UTF-8");
				$muni_names = ApiBase::getMuniNames();
				$county_names = ApiBase::getCountyNames();
				$text = "";
				$text .= self::outputWarning($results['head']);
				$text .= self::writeHeader();
				foreach($results['body'] as $row)
					$text .= self::writeRow($row, $muni_names, $county_names);
				$text .= self::writeEnder();
				
				#print
				echo $text;
			}
		}
	}
?>