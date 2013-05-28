<?php	
	/*
	 * Creates a KML file of the desired output
	 */
	class FormatKml{
		private function initialise(){
			/* Setting XML header */
			@header ("content-type: text/xml charset=UTF-8");
			/* Initializing the XML Object */			
			$xml = new XmlWriter();
			$xml->openMemory();
			$xml->setIndent(true);
			$xml->setIndentString('    ');
			$xml->startDocument('1.0', 'UTF-8');
			$xml->startElement('kml');
			$xml->writeAttribute('xmlns','http://www.opengis.net/kml/2.2');
			
			#Setting document properties
			$xml->startElement('Document');
				$xml->startElement('Style');
				$xml->writeAttribute('id','monumentStyle');
					$xml->startElement('IconStyle');
					$xml->writeAttribute('id','monumentIcon');
						$xml->startElement('Icon');
							$xml->startElement('href');
								$xml->text('http://maps.google.com/mapfiles/kml/paddle/ylw-blank.png');
							$xml->endElement();
						$xml->endElement();
					$xml->endElement();
				$xml->endElement();
				$xml->startElement('Style');
				$xml->writeAttribute('id','monPicStyle');
					$xml->startElement('IconStyle');
					$xml->writeAttribute('id','monPicIcon');
						$xml->startElement('Icon');
							$xml->startElement('href');
								$xml->text('http://maps.google.com/mapfiles/kml/paddle/blu-circle.png');
							$xml->endElement();
						$xml->endElement();
					$xml->endElement();
				$xml->endElement();
			return ($xml);
		}
		
		private function finalise(XMLWriter $xml){
			/* Closing last XML nodes */
			$xml->endElement(); #end Document
			$xml->endElement(); #end kml
		}
		
		private function writeRow(XMLWriter $xml, $row, $muni_names){
			$row = $row['hit'];
			#Ignore rows without coords
			if (!empty($row['lat']) and !empty($row['lon'])){
				$xml->startElement('Placemark');
				$placemarkId = $row['source'].$row['id'];
				$xml->writeAttribute('id',htmlspecialchars( $placemarkId ));
					if (!empty($row['title'])){
						$xml->startElement('title');
							$xml->text(htmlspecialchars( $row['title'] ));
						$xml->endElement();
					}
					$xml->startElement('description');
						$desc = '';
						if (!empty($row['image'])){
							$imgsize = 100;
							$desc .= '<a href="http://commons.wikimedia.org/wiki/File:' . rawurlencode($row['image']) . '">';
							$desc .= '<img src="' . ApiBase::getImageFromCommons($row['image'],$imgsize) . '" align="right" />';
							$desc .= '</a>';
							$styleUrl = '#monPicStyle';
			            }else
				            $styleUrl = '#monumentStyle';
			            $desc .= '<ul>';
			            if (!empty($row['title'])){
							$desc .= '<li> '; #title
							$desc .= '<b>'.htmlspecialchars($row['title']).'</b>';
							$desc .= '</li>';
						}
			            $desc .= '<li> '; #artist - year
			            $artist_info = ApiBase::getArtistInfo($row['id']);
			            if (!empty($artist_info)){
							foreach ($artist_info as $ai){
								if($ai['wiki']){
									#$desc .= '<a href="https://wikidata.org/wiki/' . rawurlencode($ai['wiki']) . '">';
									$desc .= '<a href="'.ApiBase::getArticleFromWikidata($ai['wiki']).'">';
									$desc .= ''.htmlspecialchars($ai['name']);
									$desc .= '</a>';
								} else
									$desc .= ''.htmlspecialchars($ai['name']);
								$desc .= ', ';
							}
							$desc = substr($desc, 0, -2); #remove trailing ","
							if (!empty($row['year']))
								$desc .= ' - '.htmlspecialchars($row['year']);
						}
			            elseif (!empty($row['artist'])){
							$desc .= htmlspecialchars($row['artist']);
							if (!empty($row['year']))
								$desc .= ' - '.htmlspecialchars($row['year']);
						}elseif (!empty($row['year']))
								$desc .= htmlspecialchars($row['year']);
						$desc .= '</li><li> '; #Muni - address
						$desc .= htmlspecialchars($muni_names[$row['muni']]);
						if (!empty($row['district']))
							$desc .= ' ('.htmlspecialchars($row['district']).')';
						if (!empty($row['address']))
								$desc .= ' - '.htmlspecialchars($row['address']);
						$desc .= '</li><li> '; #Description
						if (!empty($row['descr']))
								$desc .= '<br/>'.htmlspecialchars($row['descr']);
						if (!empty($row['wiki_article'])){
							$desc .= '</li><br/><li>'.htmlspecialchars('Läs mer om konstverket på ');
							#$desc .= '<a href="https://wikidata.org/wiki/' . rawurlencode($row['wiki_article']) . '">';
							$desc .= '<a href="'.ApiBase::getArticleFromWikidata($row['wiki_article']).'">';
							$desc .= 'Wikipedia';
							$desc .= '</a>.';
						}
						$desc .= '</li></ul>';
						$desc .= '</ul>';
						$xml->writeCData($desc);
					$xml->endElement();
					$xml->startElement('styleUrl');
						$xml->text($styleUrl);
					$xml->endElement();
					$xml->startElement('Point');
						$xml->startElement('coordinates');
							$xml->text($row['lon'].','.$row['lat']);
						$xml->endElement();
					$xml->endElement();
				$xml->endElement();
			}
		}
		
		function output($results){
			if($results['head']['status'] == '0') #Fall back to xml if errors
				Format::outputXml($results);
			else{
				$xml = self::initialise();
				
				#Output each row in the body
				$muni_names = ApiBase::getMuniNames();
				foreach($results['body'] as $row)
					self::writeRow($xml, $row, $muni_names);
					
				#finalise
				self::finalise($xml);
				#print
				echo $xml->outputMemory(true);
			}
		}
	}
?>